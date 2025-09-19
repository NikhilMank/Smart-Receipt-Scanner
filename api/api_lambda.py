import json
import boto3
from decimal import Decimal
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Receipts')
users_table = dynamodb.Table('Users')

def decimal_default(obj):
    """JSON serializer for Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def cors_headers():
    """Return CORS headers for all responses"""
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    }

def get_user_from_token(event):
    """Extract user ID from request context (API Gateway handles JWT verification)"""
    try:
        # API Gateway puts Cognito user info in requestContext
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        claims = authorizer.get('claims', {})
        user_id = claims.get('sub')  # Cognito user ID
        
        # Validate user_id format (should be UUID)
        if user_id and len(user_id) > 10 and '-' in user_id:
            return user_id
        else:
            print(f"Invalid user_id format from JWT: {user_id}")
            return None
    except Exception as e:
        print(f"Error extracting user_id from token: {e}")
        return None

def lambda_handler(event, context):
    """
    API Gateway Lambda function to query receipt data
    Supports endpoints:
    - POST /auth/register - Register new user
    - POST /auth/login - Login user
    - GET /receipts - List user receipts with optional filters
    - GET /receipts/{id} - Get specific user receipt
    - GET /analytics/summary - Get user spending summary by category
    - GET /analytics/monthly - Get user monthly spending trends
    """
    
    try:
        http_method = event['httpMethod']
        path = event['path']
        query_params = event.get('queryStringParameters') or {}
        path_params = event.get('pathParameters') or {}
        
        # Public endpoints (no auth required)
        if path == '/test' and http_method == 'GET':
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({'message': 'API is working', 'timestamp': datetime.now().isoformat()})
            }
        elif path == '/auth/register' and http_method == 'POST':
            return register_user(event)
        elif path == '/auth/login' and http_method == 'POST':
            return login_user(event)
        
        # Protected endpoints (auth required)
        user_id = get_user_from_token(event)
        if not user_id:
            return {
                'statusCode': 401,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Unauthorized'})
            }
        
        if path == '/receipts' and http_method == 'GET':
            return get_receipts(query_params, user_id)
        elif path.startswith('/receipts/') and http_method == 'GET':
            receipt_id = path_params.get('id')
            return get_receipt_by_id(receipt_id, user_id)
        elif path == '/analytics/summary' and http_method == 'GET':
            return get_spending_summary(query_params, user_id)
        elif path == '/analytics/monthly' and http_method == 'GET':
            return get_monthly_trends(query_params, user_id)
        elif path == '/analytics/metrics' and http_method == 'GET':
            return get_key_metrics(query_params, user_id)
        elif path == '/analytics/patterns' and http_method == 'GET':
            return get_spending_patterns(query_params, user_id)
        elif path == '/upload/presigned-url' and http_method == 'POST':
            return get_presigned_upload_url(event, user_id)
        elif http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS',
                    'Access-Control-Max-Age': '86400'
                },
                'body': ''
            }
        else:
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Endpoint not found'})
            }
            
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def register_user(event):
    """Register new user with Cognito"""
    try:
        import boto3
        
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')
        name = body.get('name', '')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Email and password required'})
            }
        
        cognito = boto3.client('cognito-idp')
        
        # Create user with temporary password
        response = cognito.admin_create_user(
            UserPoolId='eu-central-1_Eg9Fy4q8u',
            Username=email,
            UserAttributes=[
                {'Name': 'email', 'Value': email},
                {'Name': 'name', 'Value': name},
                {'Name': 'email_verified', 'Value': 'true'}
            ],
            TemporaryPassword='TempPass123!',
            MessageAction='SUPPRESS'
        )
        
        # Set permanent password directly
        cognito.admin_set_user_password(
            UserPoolId='eu-central-1_Eg9Fy4q8u',
            Username=email,
            Password=password,
            Permanent=True
        )
        
        user_id = response['User']['Username']
        
        # Try to store in Users table, but don't fail if table doesn't exist
        try:
            users_table.put_item(
                Item={
                    'user_id': user_id,
                    'email': email,
                    'name': name,
                    'created_at': datetime.now().isoformat()
                }
            )
        except Exception as table_error:
            print(f"Users table error (non-critical): {table_error}")
        
        return {
            'statusCode': 201,
            'headers': cors_headers(),
            'body': json.dumps({'message': 'User registered successfully', 'user_id': user_id})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def login_user(event):
    """Login user with Cognito"""
    try:
        import boto3
        import hmac
        import hashlib
        import base64
        
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Email and password required'})
            }
        
        # Generate SECRET_HASH
        client_secret = 'your_client_secret_here'  # We need to get this from Cognito
        client_id = '3uuhcnuiae6t1lavii3vfdgjnp'
        
        # For now, try without SECRET_HASH first
        cognito = boto3.client('cognito-idp')
        
        try:
            response = cognito.admin_initiate_auth(
                UserPoolId='eu-central-1_Eg9Fy4q8u',
                ClientId=client_id,
                AuthFlow='ADMIN_USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': email,
                    'PASSWORD': password
                }
            )
        except Exception as auth_error:
            # If SECRET_HASH is required, we need to disable it in Cognito
            print(f"Auth error: {auth_error}")
            return {
                'statusCode': 401,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Authentication configuration issue'})
            }
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'access_token': response['AuthenticationResult']['AccessToken'],
                'id_token': response['AuthenticationResult']['IdToken'],
                'refresh_token': response['AuthenticationResult']['RefreshToken']
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 401,
            'headers': cors_headers(),
            'body': json.dumps({'error': 'Invalid credentials'})
        }

def get_receipts(query_params, user_id):
    """Get user receipts with optional filtering"""
    try:
        # Build scan parameters with user filter
        scan_kwargs = {}
        filter_expressions = [Attr('user_id').eq(user_id)]
        
        # Filter by category
        if query_params.get('category'):
            filter_expressions.append(Attr('category').eq(query_params['category']))
        
        # Filter by date range
        if query_params.get('start_date'):
            filter_expressions.append(Attr('purchase_date').gte(query_params['start_date']))
        if query_params.get('end_date'):
            filter_expressions.append(Attr('purchase_date').lte(query_params['end_date']))
        
        # Filter by merchant
        if query_params.get('merchant'):
            filter_expressions.append(Attr('merchant').contains(query_params['merchant']))
        
        # Combine filters
        if filter_expressions:
            filter_expr = filter_expressions[0]
            if len(filter_expressions) > 1:
                for expr in filter_expressions[1:]:
                    filter_expr = filter_expr & expr
            scan_kwargs['FilterExpression'] = filter_expr
        
        # Pagination
        limit = int(query_params.get('limit', 50))
        scan_kwargs['Limit'] = min(limit, 100)  # Max 100 items
        
        if query_params.get('last_key'):
            scan_kwargs['ExclusiveStartKey'] = {'receipt_id': query_params['last_key']}
        
        response = table.scan(**scan_kwargs)
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'receipts': response['Items'],
                'count': response['Count'],
                'last_key': response.get('LastEvaluatedKey', {}).get('receipt_id')
            }, default=decimal_default)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_receipt_by_id(receipt_id, user_id):
    """Get specific receipt by ID"""
    try:
        response = table.get_item(Key={'receipt_id': receipt_id})
        
        if 'Item' not in response or response['Item'].get('user_id') != user_id:
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Receipt not found'})
            }
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps(response['Item'], default=decimal_default)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_spending_summary(query_params, user_id):
    """Get spending summary by category"""
    try:
        # Scan user receipts
        scan_kwargs = {}
        
        # Filter by user and date range if provided
        filter_expressions = [Attr('user_id').eq(user_id)]
        if query_params.get('start_date'):
            filter_expressions.append(Attr('purchase_date').gte(query_params['start_date']))
        if query_params.get('end_date'):
            filter_expressions.append(Attr('purchase_date').lte(query_params['end_date']))
        
        if filter_expressions:
            filter_expr = filter_expressions[0]
            for expr in filter_expressions[1:]:
                filter_expr = filter_expr & expr
            scan_kwargs['FilterExpression'] = filter_expr
        
        response = table.scan(**scan_kwargs)
        
        # Calculate summary by category
        category_totals = {}
        total_amount = 0
        total_receipts = 0
        
        for item in response['Items']:
            category = item.get('category', 'other')
            amount_str = item.get('total_amount', '0,00')
            
            # Convert German format (4,56) to float
            try:
                amount = float(amount_str.replace(',', '.'))
                category_totals[category] = category_totals.get(category, 0) + amount
                total_amount += amount
                total_receipts += 1
            except (ValueError, AttributeError):
                continue
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'summary': {
                    'total_amount': round(total_amount, 2),
                    'total_receipts': total_receipts,
                    'by_category': {k: round(v, 2) for k, v in category_totals.items()}
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_monthly_trends(query_params, user_id):
    """Get monthly spending trends with category breakdown"""
    try:
        # Scan user receipts
        response = table.scan(
            FilterExpression=Attr('user_id').eq(user_id)
        )
        
        # Group by month and category
        monthly_data = {}
        
        for item in response['Items']:
            purchase_date = item.get('purchase_date')
            if not purchase_date:
                continue
                
            try:
                # Parse different date formats
                month_key = None
                
                if '-' in purchase_date and len(purchase_date) == 10:
                    # ISO format: YYYY-MM-DD
                    month_key = purchase_date[:7]  # YYYY-MM
                elif '.' in purchase_date:
                    # German format: DD.MM.YYYY
                    parts = purchase_date.split('.')
                    if len(parts) == 3:
                        day, month, year = parts
                        month_key = f"{year}-{month.zfill(2)}"
                
                if not month_key:
                    continue
                    
                amount_str = item.get('total_amount', '0,00')
                amount = float(amount_str.replace(',', '.'))
                category = item.get('category', 'other')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'total': 0, 'count': 0, 'categories': {}}
                
                monthly_data[month_key]['total'] += amount
                monthly_data[month_key]['count'] += 1
                
                if category not in monthly_data[month_key]['categories']:
                    monthly_data[month_key]['categories'][category] = 0
                monthly_data[month_key]['categories'][category] += amount
                
            except (ValueError, AttributeError):
                continue
        
        # Sort by month and format for stacked bar chart
        sorted_months = sorted(monthly_data.items())
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'monthly_trends': [
                    {
                        'month': month,
                        'total_amount': round(data['total'], 2),
                        'receipt_count': data['count'],
                        **{category: round(amount, 2) for category, amount in data['categories'].items()}
                    }
                    for month, data in sorted_months
                ]
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_key_metrics(query_params, user_id):
    """Get key metrics: average spending, most expensive, frequent merchant, month comparison"""
    try:
        from datetime import datetime, timedelta
        
        # Apply user and date filters
        scan_kwargs = {}
        filter_expressions = [Attr('user_id').eq(user_id)]
        if query_params.get('start_date'):
            filter_expressions.append(Attr('purchase_date').gte(query_params['start_date']))
        if query_params.get('end_date'):
            filter_expressions.append(Attr('purchase_date').lte(query_params['end_date']))
        
        if filter_expressions:
            filter_expr = filter_expressions[0]
            for expr in filter_expressions[1:]:
                filter_expr = filter_expr & expr
            scan_kwargs['FilterExpression'] = filter_expr
        
        response = table.scan(**scan_kwargs)
        receipts = []
        
        for receipt in response['Items']:
            try:
                amount = float(receipt.get('total_amount', '0,00').replace(',', '.'))
                receipts.append({
                    'amount': amount,
                    'merchant': receipt.get('merchant', ''),
                    'date': receipt.get('purchase_date', '')
                })
            except:
                continue
        
        if not receipts:
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({
                    'metrics': {
                        'average_spending': 0,
                        'most_expensive': {'amount': 0, 'merchant': '', 'date': ''},
                        'most_frequent_merchant': {'name': '', 'count': 0},
                        'month_comparison': {'current': 0, 'previous': 0, 'change_percent': 0}
                    }
                })
            }
        
        amounts = [r['amount'] for r in receipts]
        avg_spending = sum(amounts) / len(amounts)
        
        most_expensive = max(receipts, key=lambda x: x['amount'])
        
        merchant_counts = {}
        for r in receipts:
            merchant = r['merchant'] or 'Unknown'
            merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1
        
        most_frequent = max(merchant_counts.items(), key=lambda x: x[1]) if merchant_counts else ('', 0)
        
        # Simple month comparison
        now = datetime.now()
        current_month = now.strftime('%Y-%m')
        prev_month = (now.replace(day=1) - timedelta(days=1)).strftime('%Y-%m')
        
        current_total = sum(r['amount'] for r in receipts if current_month in r['date'])
        prev_total = sum(r['amount'] for r in receipts if prev_month in r['date'])
        
        change_percent = ((current_total - prev_total) / prev_total * 100) if prev_total > 0 else 0
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'metrics': {
                    'average_spending': round(avg_spending, 2),
                    'most_expensive': {
                        'amount': round(most_expensive['amount'], 2),
                        'merchant': most_expensive['merchant'],
                        'date': most_expensive['date']
                    },
                    'most_frequent_merchant': {
                        'name': most_frequent[0],
                        'count': most_frequent[1]
                    },
                    'month_comparison': {
                        'current': round(current_total, 2),
                        'previous': round(prev_total, 2),
                        'change_percent': round(change_percent, 1)
                    }
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def get_spending_patterns(query_params, user_id):
    """Get spending patterns: weekday vs weekend, predictions"""
    try:
        from datetime import datetime
        
        # Apply user and date filters
        scan_kwargs = {}
        filter_expressions = [Attr('user_id').eq(user_id)]
        if query_params.get('start_date'):
            filter_expressions.append(Attr('purchase_date').gte(query_params['start_date']))
        if query_params.get('end_date'):
            filter_expressions.append(Attr('purchase_date').lte(query_params['end_date']))
        
        if filter_expressions:
            filter_expr = filter_expressions[0]
            for expr in filter_expressions[1:]:
                filter_expr = filter_expr & expr
            scan_kwargs['FilterExpression'] = filter_expr
        
        response = table.scan(**scan_kwargs)
        weekday_total = weekend_total = 0
        weekday_count = weekend_count = 0
        monthly_totals = {}
        
        for receipt in response['Items']:
            try:
                amount = float(receipt.get('total_amount', '0,00').replace(',', '.'))
                date_str = receipt.get('purchase_date', '')
                
                # Parse date
                receipt_date = None
                if '-' in date_str and len(date_str) == 10:
                    receipt_date = datetime.strptime(date_str, '%Y-%m-%d')
                elif '.' in date_str:
                    parts = date_str.split('.')
                    if len(parts) == 3:
                        day, month, year = parts
                        if len(year) == 2:
                            year = '20' + year
                        receipt_date = datetime(int(year), int(month), int(day))
                
                if receipt_date:
                    if receipt_date.weekday() < 5:
                        weekday_total += amount
                        weekday_count += 1
                    else:
                        weekend_total += amount
                        weekend_count += 1
                    
                    month_key = receipt_date.strftime('%Y-%m')
                    monthly_totals[month_key] = monthly_totals.get(month_key, 0) + amount
                    
            except:
                continue
        
        # Simple prediction based on last 3 months average
        sorted_months = sorted(monthly_totals.items())[-3:]
        avg_monthly = sum(total for _, total in sorted_months) / len(sorted_months) if sorted_months else 0
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'patterns': {
                    'weekday_vs_weekend': {
                        'weekday_total': round(weekday_total, 2),
                        'weekend_total': round(weekend_total, 2),
                        'weekday_avg': round(weekday_total / weekday_count, 2) if weekday_count > 0 else 0,
                        'weekend_avg': round(weekend_total / weekend_count, 2) if weekend_count > 0 else 0
                    },
                    'prediction': {
                        'next_month_forecast': round(avg_monthly, 2),
                        'based_on_months': len(sorted_months)
                    }
                }
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }
def get_presigned_upload_url(event, user_id):
    """Generate presigned URL for S3 upload"""
    try:
        import boto3
        import uuid
        import json
        
        # Validate user_id
        if not user_id or user_id == 'None':
            return {
                'statusCode': 401,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Invalid user authentication'})
            }
        
        body_str = event.get('body', '{}')
        if not body_str:
            body_str = '{}'
        body = json.loads(body_str)
        filename = body.get('filename', 'receipt.jpg')
        content_type = body.get('contentType', 'image/jpeg')
        
        # Generate unique filename with user_id
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"receipts/{user_id}/{uuid.uuid4()}.{file_extension}"
        
        # Create S3 client
        s3_client = boto3.client('s3')
        bucket_name = 'receipt-scanner-nikhil-dev'
        
        # Generate presigned URL
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': unique_filename,
                'ContentType': content_type
            },
            ExpiresIn=3600  # 1 hour
        )
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'uploadUrl': presigned_url,
                'key': unique_filename,
                'bucket': bucket_name
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }