from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)
CORS(app)

AWS_ACCESS_KEY_ID = 'AKIA6G75DYUUCBTK76G7'
AWS_SECRET_ACCESS_KEY = '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'
AWS_REGION = 'ap-south-1'
S3_BUCKET = 'digikendr'

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

@app.route('/upload', methods=['POST'])
def upload_files():
    files = request.files.getlist('files')
    filenames = request.form.getlist('filenames')

    if not files or not filenames:
        print("Error: Missing files or filenames")
        return jsonify({'error': 'Missing files or filenames'}), 400

    if len(files) != len(filenames):
        print(f"Error: Number of files ({len(files)}) and filenames ({len(filenames)}) do not match")
        return jsonify({'error': 'Number of files and filenames must match'}), 400

    uploaded_urls = []

    for index, (file, custom_filename) in enumerate(zip(files, filenames)):
        if custom_filename.strip() == '':
            print(f"Warning: Skipping file at index {index} due to blank filename")
            continue  # skip blank filenames

        try:
            content_type = file.content_type or 'application/octet-stream'

            s3_client.upload_fileobj(
                file,
                S3_BUCKET,
                custom_filename,
                ExtraArgs={
                    'ContentType': content_type
                }
            )

            url = f"https://{S3_BUCKET}.s3.{AWS_REGION}.amazonaws.com/{custom_filename}"
            uploaded_urls.append(url)
            print(f"Uploaded: {custom_filename} -> {url}")

        except ClientError as e:
            error_msg = f"Upload failed for {custom_filename}: {e}"
            print(error_msg)
            app.logger.error(error_msg)

    if not uploaded_urls:
        print("Error: No files were uploaded")
        return jsonify({'error': 'No files were uploaded'}), 500

    return jsonify({'uploaded_urls': uploaded_urls}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
