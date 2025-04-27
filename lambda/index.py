import json  
import os  
import urllib.request  
import urllib.error  
import urllib.parse  
  
# グローバル変数  
API_ENDPOINT = os.environ.get('API_ENDPOINT', 'https://08ed-35-247-171-100.ngrok-free.app')  
  
def lambda_handler(event, context):  
    try:  
        print("Received event:", json.dumps(event))  
          
        # Cognitoで認証されたユーザー情報を取得  
        user_info = None  
        if 'requestContext' in event and 'authorizer' in event['requestContext']:  
            user_info = event['requestContext']['authorizer']['claims']  
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")  
          
        # リクエストボディの解析  
        body = json.loads(event['body'])  
        message = body['message']  
        conversation_history = body.get('conversationHistory', [])  
          
        print("Processing message:", message)  
          
        # 会話履歴を使用してプロンプトを構築  
        # 簡単な例として、最後のユーザーメッセージのみを使用  
        prompt = message  
          
        # 提供されたAPIフォーマットに合わせてリクエストペイロードを作成  
        request_payload = {  
            "prompt": prompt,  
            "max_new_tokens": 512,  
            "do_sample": True,  
            "temperature": 0.7,  
            "top_p": 0.9  
        }  
          
        print("Calling external API with payload:", json.dumps(request_payload))  
          
        # urllib.requestを使用してAPIを呼び出す  
        req = urllib.request.Request(  
            url=API_ENDPOINT,  
            data=json.dumps(request_payload).encode('utf-8'),  
            headers={  
                'Content-Type': 'application/json'  
            },  
            method='POST'  
        )  
          
        try:  
            with urllib.request.urlopen(req) as response:  
                response_data = response.read()  
                response_body = json.loads(response_data.decode('utf-8'))  
                print("API response:", json.dumps(response_body, default=str))  
                  
                # レスポンスの解析（APIによって異なる）  
                # 応答形式に合わせて調整が必要かもしれません  
                assistant_response = response_body.get('generated_text', '')  
                  
                if not assistant_response:  
                    raise Exception("No response content from the model")  
                  
                # 会話履歴を更新  
                messages = conversation_history.copy()  
                # ユーザーメッセージを追加  
                messages.append({  
                    "role": "user",  
                    "content": message  
                })  
                # アシスタントの応答を追加  
                messages.append({  
                    "role": "assistant",  
                    "content": assistant_response  
                })  
                  
                # 成功レスポンスの返却  
                return {  
                    "statusCode": 200,  
                    "headers": {  
                        "Content-Type": "application/json",  
                        "Access-Control-Allow-Origin": "*",  
                        "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",  
                        "Access-Control-Allow-Methods": "OPTIONS,POST"  
                    },  
                    "body": json.dumps({  
                        "success": True,  
                        "response": assistant_response,  
                        "conversationHistory": messages  
                    })  
                }  
        except urllib.error.HTTPError as e:  
            error_message = e.read().decode('utf-8')  
            print(f"HTTP Error: {e.code} - {error_message}")  
            raise Exception(f"API request failed: {e.code} - {error_message}")  
        except urllib.error.URLError as e:  
            print(f"URL Error: {e.reason}")  
            raise Exception(f"API connection failed: {e.reason}")  
              
    except Exception as error:  
        print("Error:", str(error))  
          
        return {  
            "statusCode": 500,  
            "headers": {  
                "Content-Type": "application/json",  
                "Access-Control-Allow-Origin": "*",  
                "Access-Control-Allow-Headers": "Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token",  
                "Access-Control-Allow-Methods": "OPTIONS,POST"  
            },  
            "body": json.dumps({  
                "success": False,  
                "error": str(error)  
            })  
        }
