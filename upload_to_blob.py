import os
import sys
import datetime
import requests
import base64
import hmac
import hashlib
import argparse
from time import time, sleep
from azure.storage.blob import BlobServiceClient, BlobClient, ContentSettings
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
from dotenv import load_dotenv


def generate_auth_header(storageKey, accountName, storageName, method, blobName, fileSize, currentDate, contentType):

    headerArrResource = {
        'x-ms-blob-cache-control': 'max-age=3600',
        "x-ms-blob-type": "BlockBlob",
        "x-ms-date": currentDate,
        "x-ms-version": "2015-12-11"
    }
    headerResource = "\n".join(f"{k}:{v}" for k, v in headerArrResource.items())
    urlResource = f"/{accountName}/{storageName}/{blobName}"

    
    signatureArrResource = [
        method,               #HTTP Verb*/
        '',                  #Content-Encoding*/
        '',                  #Content-Language*/
        fileSize,          #Content-Length (include value when zero)*/
        '',                  #Content-MD5*/
        contentType,         #Content-Type*/
        '',                  #Date*/
        '',                  #If-Modified-Since */
        '',                  #If-Match*/
        '',                  #If-None-Match*/
        '',                  #If-Unmodified-Since*/
        '',                  #Range*/
        headerResource,      #CanonicalizedHeaders*/
        urlResource,         #CanonicalizedResource*/
    ]
    
    signatureStrResource = "\n".join(signatureArrResource)
    signed_string = base64.b64encode(hmac.new(base64.b64decode(storageKey), signatureStrResource.encode("utf-8"), hashlib.sha256).digest()).decode("utf-8")
    authorization_header = f"SharedKey {accountName}:{signed_string}"

    return authorization_header

def count_zip_files(directory_path):
    zip_file_count = 0

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.lower().endswith(".zip"):
                zip_file_count += 1

    return zip_file_count

def upload_to_azure_blob(storageKey, accountName, storageName, fileToUpload, blobName, fileSize, destinationUrl, contentType):
    
    currentDate = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
    
    authorization_header = generate_auth_header(storageKey, accountName, storageName, 'PUT', blobName, fileSize, currentDate, contentType)
    headers={
        "Authorization": authorization_header,
        "x-ms-blob-cache-control": "max-age=3600",
        "x-ms-blob-type": "BlockBlob",
        "x-ms-date": currentDate,
        "x-ms-version": "2015-12-11",
        "Content-Type": contentType,
        "Content-Length": fileSize,
    }
    response = requests.put(
        destinationUrl, 
        data=fileToUpload, 
        headers=headers, 
    )

    if response.status_code == 201:
        log_message(f"Uploaded: {blobName} to Azure Blob Storage successfully.")
        return True
    else:
        log_message(f"Failed to upload {blobName} - Status code: {response.status_code}")
    
    return False

def upload_blob_service_to_azure_blob(storageKey, accountName, storageName, fileToUpload, blobName, fileSize, destinationUrl, contentType):
    try:
        # Initialize the BlobServiceClient
        blob_service_client = BlobServiceClient(account_url=f"https://{accountName}.blob.core.windows.net", credential=storageKey)

        # Get a reference to the container
        container_client = blob_service_client.get_container_client(storageName)

        # Upload the blob with overwrite=True to enable overwriting if the blob already exists
        blob_client = container_client.get_blob_client(blobName)
        response = blob_client.upload_blob(data=fileToUpload, overwrite=True, content_settings=ContentSettings(content_type=contentType))
        #container_client.upload_blob(name=blobName, data=fileToUpload, content_settings=ContentSettings(content_type=contentType))
        log_message(f"Uploaded: {blobName} to Azure Blob Storage successfully.")
        return True
    
    except ResourceNotFoundError as not_found_error:
        # Handle the case where the container or blob does not exist
        log_message(f"Resource not found error: {not_found_error}")
    except HttpResponseError as http_error:
        # Handle other HTTP response errors (e.g., access denied, invalid credentials)
        log_message(f"HTTP response error: {http_error}")
    except Exception as e:
        # Handle other exceptions
        log_message(f"Failed to upload {blobName}. {str(e)}")
    finally:
        return False

def upload_large_file_to_azure_blob(storageKey, accountName, storageName, fileToUpload, blobName, fileSize, destinationUrl, contentType):
    currentDate = datetime.datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    authorization_header = generate_auth_header(storageKey, accountName, storageName, 'PUT', blobName, fileSize, currentDate, contentType)
    headers = {
        "Authorization": authorization_header,
        "x-ms-blob-cache-control": "max-age=3600",
        "x-ms-blob-type": "BlockBlob",
        "x-ms-date": currentDate,
        "x-ms-version": "2015-12-11",
        "Content-Type": contentType,
        "Content-Length": fileSize,
    }
    
    response = requests.put(
        destinationUrl,
        headers=headers,
        data="",
    )
    
    if response.status_code == 201:
        log_message(f"Initialized upload session for {blobName}.")
    else:
        log_message(f"Failed to initialize upload session for {blobName}. Status code: {response.status_code}")
        return False
    
    offset = 0
    block_number = 1
    chunk_size = 99 * 1024 * 1024  # 100 MB chunks (adjust as needed)
    
    with open(fileToUpload, "rb") as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            
            response = requests.put(
                f"{destinationUrl}&comp=block&blockid={block_number:08x}",
                headers={
                    "Authorization": authorization_header,
                    "x-ms-date": currentDate,
                    "x-ms-version": "2015-12-11",
                    "Content-Length": str(len(chunk)),
                    "Content-Type": contentType,
                },
                data=chunk,
            )
            
            if response.status_code == 201:
                log_message(f"Uploaded chunk {block_number} for {blobName}.")
            else:
                log_message(f"Failed to upload chunk {block_number} for {blobName}. Status code: {response.status_code}")
                return
            
            offset += chunk_size
            block_number += 1
    
    # Commit the blob after uploading all chunks
    response = requests.put(
        f"{destinationUrl}&comp=blocklist",
        headers={
            "Authorization": authorization_header,
            "x-ms-date": currentDate,
            "x-ms-version": "2015-12-11",
            "Content-Type": contentType,
        },
        data=f"<?xml version='1.0' encoding='utf-8'?><BlockList><CommittedBlocks>{''.join([f'<Block>{block_number:08x}</Block>' for block_number in range(1, block_number)])}</CommittedBlocks></BlockList>",
    )
    
    if response.status_code == 201:
        log_message(f"Uploaded {blobName} to Azure Blob Storage successfully.")
        return True
    else:
        log_message(f"Failed to upload {blobName} - Status code: {response.status_code}")
        return False

def upload_files(account_key, account_name, container_name, container_url, directory_path, threshold_date, content_type):

    # List files in the local directory
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            blob_name = os.path.relpath(file_path, directory_path)
            # Get the file's last modified timestamp
            file_timestamp = datetime.datetime.fromtimestamp(os.path.getctime(file_path))

            # Check if the file was modified threshold day/s ago 
            if file.lower().endswith('zip'):
                if file_timestamp < threshold_date:
                    blob_url = f"{container_url}/{blob_name}"
                    fileSize = str(os.path.getsize(file_path))
                    
                    log_message(f"Uploading: {blob_name} | {(fileSize)}")
                    isUploadSuccess = False
                    with open(file_path, "rb") as data: 
                        if is_large_file(file_path):
                            isUploadSuccess = upload_blob_service_to_azure_blob(account_key, account_name, container_name, data, blob_name, fileSize, blob_url, content_type)
                        else:
                            isUploadSuccess = upload_blob_service_to_azure_blob(account_key, account_name, container_name, data, blob_name, fileSize, blob_url, content_type)
                    
                    if isUploadSuccess:
                        log_message(f"Deleting: {blob_name} | {file_path}")
                        sleep(1)
                        os.remove(file_path)
                        log_message(f"Successfully Deleted: {blob_name}")

                else:
                    log_message(f"Skipping: {blob_name} | {file_timestamp} | {threshold_date}")

    log_message("Upload completed.")

def is_large_file(file_path, size_limit=100 * 1024 * 1024):  # 100 MB in bytes
    file_size = os.path.getsize(file_path)
    return file_size > size_limit

def log_message(message):
    now = datetime.datetime.utcnow()
    utctime = (now.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"[{utctime}] {message}")

def main():
    parser = argparse.ArgumentParser(description="Upload files to Azure Blob Storage")
    parser.add_argument("--directory", required=True, help="Local directory path to upload")
    parser.add_argument("--container", required=True, help="Azure Blob Storage container name")
    parser.add_argument("--threshold", required=True, help="Threshold date by days")
    parser.add_argument("--content_type", required=True, help="Content Type of the file")
    args = parser.parse_args()

    # Load environment variables from the .env file
    dotenv_path = '/boot/azure_blob/azure.env'
    # dotenv_path = './environment/azure.env'
    load_dotenv(dotenv_path)

    # Azure Blob Storage account settings
    # Access the environment variables
    account_name = os.getenv('ACCOUNT_NAME')
    account_key = os.getenv('ACCOUNT_KEY')

    if account_name is None and account_key is None:
        log_message("Credentials not set")
        sys.exit(0)

    # container_name = "backup-poc"
    directory_path = args.directory
    container_name = args.container
    threshold_days = args.threshold
    content_type = args.content_type

    container_url = f"https://{account_name}.blob.core.windows.net/{container_name}"
    
    # Calculate the date one day ago
    threshold_date = datetime.datetime.now() - datetime.timedelta(days=int(threshold_days))
    try:
        if count_zip_files(directory_path) > 0:
            upload_files(account_key, account_name, container_name, container_url, directory_path, threshold_date, content_type)

        else:
            log_message("No Zip Files")
    except KeyboardInterrupt:
        # Handle Ctrl + C gracefully
        print("Ctrl + C pressed. Exiting gracefully...")
        sys.exit(0)  # Exit with a status code indicating successful termination
    except Exception as e:
        # Handle other exceptions
        print(f"An error occurred: {str(e)}")
        sys.exit(1)  # Exit with a non-zero status code to indicate an error

if __name__ == "__main__":
    main()