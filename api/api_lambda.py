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
        'Access-Control-Allow-Methods': 'GET, POST, PUT, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type,Authorization'
    }

def get_user_from_token(event):
    """Extract user ID from request context (API Gateway handles JWT verification)"""
    try:
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        claims = authorizer.get('claims', {})
        user_id = claims.get('sub')
        
        if user_id and len(user_id) > 10 and '-' in user_id:
            return user_id
        else:
            print(f"Invalid user_id format from JWT: {user_id}")
            return None
    except Exception as e:
        print(f"Error extracting user_id from token: {e}")
        return None

def lambda_handler(event, context):
    try:
        # Check if this is a direct profile update invocation
        if 'user_id' in event and 'monthly_budget' in event and 'httpMethod' not in event:
            print(f"Direct profile update invocation: {event}")
            # Extract user_id and treat as profile update
            user_id = event.get('user_id')
            if user_id:
                # Create a mock API Gateway event
                mock_event = {
                    'body': json.dumps(event),
                    'httpMethod': 'PUT',
                    'path': '/profile'
                }
                return update_user_profile(mock_event, user_id)
        
        # Handle both API Gateway v1 and v2 event formats
        http_method = event.get('httpMethod') or event.get('requestContext', {}).get('http', {}).get('method')
        path = event.get('path') or event.get('requestContext', {}).get('http', {}).get('path')
        query_params = event.get('queryStringParameters') or {}
        path_params = event.get('pathParameters') or {}
        
        print(f"Lambda handler called: {http_method} {path}")
        print(f"Full event keys: {list(event.keys())}")
        if path == '/profile' and http_method == 'PUT':
            print(f"Profile update request received: {event.get('body', 'No body')}")
        
        # Public endpoints
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
        
        # Protected endpoints
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
        elif path == '/profile' and http_method == 'GET':
            return get_user_profile(user_id)
        elif path == '/test-put' and http_method == 'PUT':
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps({'message': 'PUT request working', 'body': event.get('body')})
            }
        elif path == '/profile' and http_method == 'PUT':
            print(f"PUT /profile - user_id: {user_id}")
            print(f"Request context: {event.get('requestContext', {})}")
            return update_user_profile(event, user_id)
        elif http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                    'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTIONS',
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
        
        cognito.admin_set_user_password(
            UserPoolId='eu-central-1_Eg9Fy4q8u',
            Username=email,
            Password=password,
            Permanent=True
        )
        
        user_id = response['User']['Username']
        
        try:
            users_table.put_item(
                Item={
                    'user_id': user_id,
                    'email': email,
                    'name': name,
                    'monthly_budget': 0,
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
        
        body = json.loads(event.get('body', '{}'))
        email = body.get('email')
        password = body.get('password')
        
        if not email or not password:
            return {
                'statusCode': 400,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'Email and password required'})
            }
        
        cognito = boto3.client('cognito-idp')
        client_id = '3uuhcnuiae6t1lavii3vfdgjnp'
        
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
        scan_kwargs = {}
        filter_expressions = [Attr('user_id').eq(user_id)]
        
        if query_params.get('category'):
            filter_expressions.append(Attr('category').eq(query_params['category']))
        
        if query_params.get('start_date'):
            filter_expressions.append(Attr('purchase_date').gte(query_params['start_date']))
        if query_params.get('end_date'):
            filter_expressions.append(Attr('purchase_date').lte(query_params['end_date']))
        
        if query_params.get('merchant'):
            filter_expressions.append(Attr('merchant').contains(query_params['merchant']))
        
        if filter_expressions:
            filter_expr = filter_expressions[0]
            if len(filter_expressions) > 1:
                for expr in filter_expressions[1:]:
                    filter_expr = filter_expr & expr
            scan_kwargs['FilterExpression'] = filter_expr
        
        limit = int(query_params.get('limit', 50))
        scan_kwargs['Limit'] = min(limit, 100)
        
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
    """Get spending summary by category with budget comparison"""
    try:
        # Handle month filters
        start_date = query_params.get('start_date')
        end_date = query_params.get('end_date')
        
        if query_params.get('month_filter') == 'this_month':
            now = datetime.now()
            start_date = now.replace(day=1).strftime('%Y-%m-%d')
            end_date = now.strftime('%Y-%m-%d')
        elif query_params.get('month_filter') == 'last_month':
            now = datetime.now()
            last_month = now.replace(day=1) - timedelta(days=1)
            start_date = last_month.replace(day=1).strftime('%Y-%m-%d')
            end_date = last_month.strftime('%Y-%m-%d')
        
        scan_kwargs = {}
        filter_expressions = [Attr('user_id').eq(user_id)]
        if start_date:
            filter_expressions.append(Attr('purchase_date').gte(start_date))
        if end_date:
            filter_expressions.append(Attr('purchase_date').lte(end_date))
        
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
            
            try:
                amount = float(amount_str.replace(',', '.'))
                category_totals[category] = category_totals.get(category, 0) + amount
                total_amount += amount
                total_receipts += 1
            except (ValueError, AttributeError):
                continue
        
        # Get user budget
        budget = 0
        try:
            profile_response = users_table.get_item(Key={'user_id': user_id})
            print(f"Profile response for user {user_id}: {profile_response}")
            if 'Item' in profile_response:
                budget_value = profile_response['Item'].get('monthly_budget', 0)
                # Handle Decimal, string, or numeric values
                if isinstance(budget_value, Decimal):
                    budget = float(budget_value)
                elif isinstance(budget_value, str):
                    budget = float(budget_value) if budget_value else 0
                else:
                    budget = float(budget_value) if budget_value else 0
                print(f"Retrieved budget: {budget} (type: {type(budget)})")
        except Exception as e:
            print(f"Error retrieving budget: {e}")
            budget = 0
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'summary': {
                    'total_amount': round(total_amount, 2),
                    'total_receipts': total_receipts,
                    'by_category': {k: round(v, 2) for k, v in category_totals.items()},
                    'budget': budget,
                    'budget_used': round(total_amount, 2),
                    'budget_remaining': round(budget - total_amount, 2) if budget > 0 else 0
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
        response = table.scan(
            FilterExpression=Attr('user_id').eq(user_id)
        )
        
        monthly_data = {}
        
        for item in response['Items']:
            purchase_date = item.get('purchase_date')
            if not purchase_date:
                continue
                
            try:
                month_key = None
                
                if '-' in purchase_date and len(purchase_date) == 10:
                    month_key = purchase_date[:7]
                elif '.' in purchase_date:
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
    """Get key metrics"""
    try:
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
    """Get spending patterns"""
    try:
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
        
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"receipts/{user_id}/{uuid.uuid4()}.{file_extension}"
        
        s3_client = boto3.client('s3')
        bucket_name = 'receipt-scanner-nikhil-dev'
        
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': bucket_name,
                'Key': unique_filename,
                'ContentType': content_type
            },
            ExpiresIn=3600
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

def get_user_profile(user_id):
    """Get user profile information"""
    try:
        response = users_table.get_item(Key={'user_id': user_id})
        
        if 'Item' not in response:
            default_profile = {
                'user_id': user_id,
                'name': '',
                'email': '',
                'monthly_budget': 0,
                'created_at': datetime.now().isoformat()
            }
            users_table.put_item(Item=default_profile)
            return {
                'statusCode': 200,
                'headers': cors_headers(),
                'body': json.dumps(default_profile, default=decimal_default)
            }
        
        profile = response['Item']
        
        # Add monthly_budget if it doesn't exist (for existing users)
        if 'monthly_budget' not in profile:
            profile['monthly_budget'] = 0
            users_table.put_item(Item=profile)
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps(profile, default=decimal_default)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def update_user_profile(event, user_id):
    """Update user profile information"""
    try:
        body = json.loads(event.get('body', '{}'))
        print(f"Received profile update for user {user_id}: {body}")
        
        # Validate monthly_budget - convert to Decimal for DynamoDB
        monthly_budget = body.get('monthly_budget', 0)
        try:
            monthly_budget = Decimal(str(monthly_budget)) if monthly_budget is not None else Decimal('0')
        except (ValueError, TypeError):
            monthly_budget = Decimal('0')
        
        print(f"Parsed monthly_budget: {monthly_budget}")
        
        try:
            response = users_table.get_item(Key={'user_id': user_id})
            current_profile = response.get('Item', {})
            print(f"Current profile: {current_profile}")
        except Exception as e:
            print(f"Error getting current profile: {e}")
            current_profile = {}
        
        updated_profile = {
            'user_id': user_id,
            'name': body.get('name', current_profile.get('name', '')),
            'email': body.get('email', current_profile.get('email', '')),
            'monthly_budget': monthly_budget,
            'updated_at': datetime.now().isoformat()
        }
        
        if 'created_at' not in current_profile:
            updated_profile['created_at'] = datetime.now().isoformat()
        else:
            updated_profile['created_at'] = current_profile['created_at']
        
        print(f"About to save profile: {updated_profile}")
        
        try:
            # Use update_item instead of put_item for better reliability
            update_response = users_table.update_item(
                Key={'user_id': user_id},
                UpdateExpression='SET #name = :name, email = :email, monthly_budget = :budget, updated_at = :updated',
                ExpressionAttributeNames={'#name': 'name'},
                ExpressionAttributeValues={
                    ':name': updated_profile['name'],
                    ':email': updated_profile['email'],
                    ':budget': updated_profile['monthly_budget'],
                    ':updated': updated_profile['updated_at']
                },
                ReturnValues='ALL_NEW'
            )
            print(f"DynamoDB update_item response: {update_response}")
            print("Profile updated successfully in DynamoDB")
        except Exception as db_error:
            print(f"DynamoDB error: {db_error}")
            raise db_error
        
        # Verify the save by reading back
        try:
            verify_response = users_table.get_item(Key={'user_id': user_id})
            print(f"Verification read: {verify_response.get('Item', {})}")
        except Exception as verify_error:
            print(f"Verification read error: {verify_error}")
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps(updated_profile, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Full error in update_user_profile: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }