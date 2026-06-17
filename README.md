
# API list

### Authorization

> ```/api/auth/token/```

Get a token by using your `phone_number` and `password`

> ```/api/auth/token/refresh/```

Renew your access token by using you refresh token. At this time, 18th of June, refresh and access tokens last 4 and 1 days, respectively.

> ```/api/auth/begin-validation/```

Ask the server to send you a verification code to your phone number to sign up

> ```/api/auth/validate-phone-number/```

Validate your phone number through the refresh code received from the previous API and receive a user-create-key, which can be used to prove that you already validated your phone number

> ```/api/auth/create-user-via-key/```

Use the user-create-key to save your profile

> ```/api/auth/view-profile/```

View your profile

> ```/api/auth/update-profile/```

Update your profile

> ```/api/auth/update-password-request/```

Request the server to send you a verification code to update your password

> ```/api/auth/update-password/```

Use your verification code from the last API to update your password