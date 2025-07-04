from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
CORS(app)

# Your original credentials and config
AWS_ACCESS_KEY_ID = 'AKIA6G75DYUUCBTK76G7'
AWS_SECRET_ACCESS_KEY = 'Y3lIwch3vpZc56402KwuY4s41pR0QyPQFAy5LtOM'
AWS_REGION = 'ap-south-1'
S3_BUCKET = 'digikendr'

# Initialize S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'Missing files parameter'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'error': 'No files provided'}), 400

    uploaded_urls = []

    for file in files:
        if file.filename == '':
            continue  # skip blank uploads

        try:
            content_type = file.content_type or 'application/octet-stream'

            s3_client.upload_fileobj(
                file,
                S3_BUCKET,
                file.filename,
                ExtraArgs={
                    'ContentType': content_type
                }
            )

            url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{file.filename}"
            uploaded_urls.append(url)

        except ClientError as e:
            app.logger.error(f"Upload failed for {file.filename}: {e}")

    if not uploaded_urls:
        return jsonify({'error': 'No files were uploaded'}), 500

    return jsonify({'uploaded_urls': uploaded_urls}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
