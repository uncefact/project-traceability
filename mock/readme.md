# How to invoke API using Postman collection

1. Download and install Postman
2. Import the collection from this repo: mock/FastAPI.postman_collection.json
3. Open API URL in the browser : https://9idvmp0256.execute-api.ap-southeast-2.amazonaws.com/v1
4. Click on the Login link and use your GitHub account to get the access token
5. You will be redirected back to the API page where you can copy the access token printed for you
6. Now you should see the access token on the page.
8. Copy the token and set it as a current value for the customToken variable in FastAPI postman collection
9. Save the collection
10. Now you are able to run the tests using the Postman collection.
