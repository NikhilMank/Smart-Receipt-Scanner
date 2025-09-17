import json
import boto3
from decimal import Decimal
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Receipts')

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
        'Access-Control-Allow-Headers': 'Content-Type'
    }

def lambda_handler(event, context):
    """
    API Gateway Lambda function to query receipt data
    Supports endpoints:
    - GET /receipts - List all receipts with optional filters
    - GET /receipts/{id} - Get specific receipt
    - GET /analytics/summary - Get spending summary by category
    - GET /analytics/monthly - Get monthly spending trends
    """
    
    try:
        http_method = event['httpMethod']
        path = event['path']
        query_params = event.get('queryStringParameters') or {}
        path_params = event.get('pathParameters') or {}
        
        if path == '/receipts' and http_method == 'GET':
            return get_receipts(query_params)
        elif path.startswith('/receipts/') and http_method == 'GET':
            receipt_id = path_params.get('id')
            return get_receipt_by_id(receipt_id)
        elif path == '/analytics/summary' and http_method == 'GET':
            return get_spending_summary(query_params)
        elif path == '/analytics/monthly' and http_method == 'GET':
            return get_monthly_trends(query_params)
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

def get_receipts(query_params):
    """Get all receipts with optional filtering"""
    try:
        # Build scan parameters
        scan_kwargs = {}
        filter_expressions = []
        
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

def get_receipt_by_id(receipt_id):
    """Get specific receipt by ID"""
    try:
        response = table.get_item(Key={'receipt_id': receipt_id})
        
        if 'Item' not in response:
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

def get_spending_summary(query_params):
    """Get spending summary by category"""
    try:
        # Scan all receipts
        scan_kwargs = {}
        
        # Filter by date range if provided
        filter_expressions = []
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

def get_monthly_trends(query_params):
    """Get monthly spending trends"""
    try:
        # Scan all receipts (no date filtering to handle different formats)
        response = table.scan()
        
        # Group by month
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
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'total': 0, 'count': 0}
                
                monthly_data[month_key]['total'] += amount
                monthly_data[month_key]['count'] += 1
                
            except (ValueError, AttributeError):
                continue
        
        # Sort by month
        sorted_months = sorted(monthly_data.items())
        
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({
                'monthly_trends': [
                    {
                        'month': month,
                        'total_amount': round(data['total'], 2),
                        'receipt_count': data['count']
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