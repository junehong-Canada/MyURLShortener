# MyURLShortener
Design URL Shortner

### Users

### Load Balancer

### Web Servers
1. Create a Short URL (POST /urls)
```
Input: JSON payload containing the long URL {“longUrl”: “https://example.com/very-long-url"}

Output: JSON payload with the shortened URL {“shortUrl”: “https://tiny.url/3ad32p9"} and 201 Created status code.
```
If the request is invalid or malformed, we’ll return 400 Bad Request response, and in case the requested URL already exists in the system, we'll respond with 409 Conflict.

3. Redirect to Long URL (GET /urls/{shortUrlId})
```
Input: shortUrlId path parameter

Output: Response with 301 Moved Permanently and the newly created short URL in the response body as JSON { "shortUrl": "https://tiny.url/3ad32p9" }
```
301 status code instructs the browser to cache the information, which means that the next time the user types in the short URL, the browser will automatically redirect to the long URL without reaching the server.

However, if you want to track each request’s analytics and ensure it goes through your system, use the 302 status code instead.

### URL Shortener Service
- Hashing
- Auto-increment IDs
- Custom Algotithm

### Database
- MongoDB or DynamoDB
  Schema
  ```
  {
    "shortUrlId": "3ad32p9",
    "longUrl": "https://example.com/very-long-url",
    "creationDate": "2024-03-08T12:00:00Z",
    "userId": "user123",
    "clicks": 1023,
    "metadata": {
      "title": "Example Web Page",
      "tags": ["example", "web", "url shortener"],
      "expireDate": "2025-03-08T12:00:00Z"
    },
    "isActive": true
  }
  ```
- PostgreSQL for URL Shortener Service Keys
- Redis for caching
- Scaling: Combining Replication and Sharding
