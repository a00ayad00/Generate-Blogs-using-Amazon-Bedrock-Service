import boto3, botocore, json


def generate_blog_using_bedrock(topic:str) -> str:
    prompt = f''' Write a blog of about 200 words about {topic}'''

    body = {
        "prompt":prompt,
        "max_gen_len":512,
        "temperature":0.5,
        "top_p":0.9
    }

    try:
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1",
                             config = botocore.config.Config(read_timeout=300, retries={'max_attempts':3}))
        
        response = bedrock.invoke_model(body = json.dumps(body), modelId = "meta.llama3-70b-instruct-v1:0")

        response_content = response.get('body').read()
        response_data = json.loads(response_content)

        return response_data['generation']
    
    except Exception as e:
        print(f"Error generating the blog:{e}")
        return ""



def lambda_handler(event, context):
    event = json.loads(event['body'])
    blogtopic = event['blog_topic']
    generated_blog = generate_blog_using_bedrock(topic = blogtopic)

    if generated_blog:
        s3_key = f'bedrock_blogs/{blogtopic}.txt'
        s3_bucket = 'bedrock-compartment'

        s3 = boto3.client('s3')
        try:
            s3.put_object(Bucket = s3_bucket, Key = s3_key, Body = generated_blog)
            print("File saved to s3")
        except Exception as e:
            print("Error when saving the code to s3")

    else: print('No blog was genrated!!')

    return {
        'statusCode': 200,
        'body': json.dumps('Blog Generation Completed Succefully')
    }