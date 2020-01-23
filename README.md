# Message API

## Last update:  23 Jan,2019

## base url

### http://127.0.0.1:8000/
 
By using the following endpoint, URL is formed by baseurl + endpoint and API communication is performed.
For requesting API you need to add "Authorization" in request HEADER. Like: "Authorization":"token fd303bef03c9a1e199041854d1230c50ebff0735"


## Main endpoints

| Endpoint name |  Link  | Method |  Purpose|
|---|---|---|---|---|
|  Okta Signup | /signup |POST | Create user In okta domain | OK |
|  Okta Signin | /signin> |POST | User Signin | OK |
|  Activate User Account | /logout |POST | Activate new created user  | OK |
|  Okta Logout | /active-account/<str:userid> |DELETE | Logout user | OK |

|  Send Message | /sms      | POST | Send New Message Phone |
|  Create Number | /number  | POST | One number for single user |
|  Forward Message | /forward-message/<int:message_id>  | POST | Forward Message to another one |
|  Delete Number | /delete-number/<int:number_id> |DELETE | Delete created Number | OK |
|  Single chat history | /single-chat-history |GET | Get single chat history | OK |
|  Contact lists | /contact-list |GET | Get Contact lists | OK |
|  Create and get external | /external-number |GET/POST | Create and get external | OK |
|  Delete or get single external-number | /single-external-number/<str:number> | GET/DELETE | Delete or get single external-number | OK |
|  Send MMS | /mms |POST | Send MMS with media | OK |

|  Callback Data | /callback | POST | Save callback data | OK |
|  Last 10 message history | /last-10-history-list | GET | Get last 10 message history | OK |
|  Get message details | /single-history/<int:message_id> |GET | Single message details | OK |
|  Change callback URL | /change-callback-url |POST | Change default callback URL | OK |
|  Notifications | /get-notifications |GET | Get last 10 notifications | OK |
|  P2P Chat history| /accountnumbers/<str:e164>/conversations/<str:number> |GET | Get P2P Chat history | OK |
|  Upload image| /upload |POST | Upload image for send MMS | OK |
|  Get list or Delete external-number /single-external-number/<str:number> |GET/Delete | Get list or Delete external numbers | OK |


## Endpoint detail:

###HTTP REQUEST :  **POST  /signup**

###### params
```json
{
	"firstname": "islando",
	"lastname": "cooper",
	"email": "gopu@quick-mail.online",
	"password": "Testoktauser2019"
}
```

| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| firstname   | true | |
| lastname    | true | |
| email       | true | |
| password    | true | |

###### output

### possible response list:

1. HTTP_201 Created----- Successfully added


``` json
{
    "success": "Your account is successfully created!.Please check your email to activate your account."
}
```

###HTTP REQUEST :  **POST  /signin**

###### params
```json
{
	"email": "fukugalum@virtual-email.comm",
	"password": "Testoktauser2019"
}
```

| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| email      | true | |
| password   | true | |

###### output

### possible response list:

1. HTTP_201 Created----- Successfully added


``` json
{
    "expiresAt": "2019-04-27T04:06:42.000Z",
    "status": "SUCCESS",
    "sessionToken": "102mrf8Ps9BTPuHnDCJ7530xQ",
    "_embedded": {
        "user": {
            "id": "00uk5bi2tj3ovBqHA0h7",
            "passwordChanged": "2019-04-05T11:46:02.000Z",
            "profile": {
                "login": "ashique00004@gmail.com",
                "firstName": "Ashique",
                "lastName": "00004",
                "locale": "en",
                "timeZone": "America/Los_Angeles"
            }
        }
    }
}
```

###HTTP REQUEST :  **POST  /active-account/<str:userid>**

###### params
```json

```

| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| email   | true | |
| password   | true | |

###### output

### possible response list:

1. HTTP_201 Created----- Successfully added


``` json
{
    "success": "Your account is successfully activated!."
}
```

###HTTP REQUEST :  **DELETE  /signout**

###### params
```json
{
  "Authorization": "Bearer VZaraI0ETfylr1J6gazqA9bnXZV7U"
}
```

| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| Authorization   | true | |

###### output

### possible response list:

1. HTTP_204_NO_CONTENT----- NO_CONTENT
``` json
{
    
}
```

###HTTP REQUEST :  **POST  /sms**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "message":"Good morning, this is a test message",
     "message_to": "+14676876847",
     "message_from": "+11116876847",
     "media": "image.phg"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| message      | true | | 
| message_to   | true | | 
| message_from | true | | 

###### output
``` json 
{
}
``` 

###HTTP REQUEST :  **POST  /number**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params
```json 
{    
     "number":"+182654987"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| number      | true | | 

###### output
``` json 
{
    "id": "9dcaac06-6040-42e5-a5f6-6dac18b57c11",
    "user": 1,
    "number": "+198765437441"
}
``` 

###HTTP REQUEST :  **POST  /forward-message/<int:message_id>**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "forward_number":"+1-940-220-9677",
     "message_from": "+11116876847",
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| forward_number | true | | 
| message_from   | true | | 
| message_id     | true | | 

###### output
``` json 
{

}
``` 

###HTTP REQUEST :  **DELETE  /delete-number/<int:number_id>**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "number_id":"+1-940-220-9677",
     "user_id": "2"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| number_id | true | | 
| user_id     | true | | 

###### output
``` json 
{
    'message': 'Number deleted!'
}
``` 

###HTTP REQUEST :  **POST  /single-chat-history**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "my_number":"+1-000-0000-9677",
     "contact_number": "+1-940-220-0000"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| my_number      | true | | 
| contact_number | true | | 

###### output
``` json 
{
    "results": [
        {
            "id": 43,
            "text": "forhad 88",
            "time": "2019-04-20T05:50:16.803321Z",
            "state": "send",
            "message_from": [
                "+19402209677"
            ],
            "message_to": [
                "+12816388201"
            ]
        },
        {
            "id": 42,
            "text": "forhad 88",
            "time": "2019-04-20T05:49:38.535695Z",
            "state": "send",
            "message_from": [
                "+19402209677"
            ],
            "message_to": [
                "+12816388201"
            ]
        }
    ],
    "count": 2
}
``` 

###HTTP REQUEST :  **GET  /contact-list**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "user_id":"1"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| user_id      | true | |  

###### output
``` json 
{
    "results": [
        {
            "my_number": "+19402209677",
            "contact_number": "+12816388201"
        }
    ]
}
``` 

###HTTP REQUEST :  **POST  /external-number**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "system_number":"+19402209677",
     'cell_phone': '+12818454250'
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| system_number   | true | |  
| cell_phone      | true | |  

###### output
``` json 

``` 

###HTTP REQUEST :  **GET  /external-number**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "user_id":"1"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| user_id   | true | |  

###### output
``` json 
{
    "next": null,
    "previous": null,
    "count": 0,
    "limit": 20,
    "results": [
     {
        'number': 1,
        'source': '+164767987899'
        'e164': '+14646465465'
     }
    ]
}
``` 

###HTTP REQUEST :  **GET  /single-external-number/<str:number>**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "number": "+16656989775"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| number   | true | |  

###### output
``` json 
{
    "next": null,
    "previous": null,
    "count": 0,
    "limit": 20,
    "results": [
     {
        'number': 1,
        'source': '+164767987899'
        'e164': '+14646465465'
     }
    ]
}
``` 

###HTTP REQUEST :  **DELETE  /single-external-number/<str:number>**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "number": "+16656989775"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| number   | true | |  

###### output
``` json 

``` 

###HTTP REQUEST :  **POST  /mms**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
    'message': "sending MMS",
    'message_to': "2818454250",
    'number_id': "17", 
    'media': "https://images.pexels.com/photos/2162909/clouds-crescent-moon-daylight-2162909.jpg&fm=jpg,https://images.pexels.com/photos/2170473/beautiful-mobile-wallpaper-motion-2170473.jpg&fm=jpg"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| message      | true | |  
| message_to   | true | |  
| number_id    | true | |  
| media        | true | |  

###### output
``` json 

``` 

###HTTP REQUEST :  **POST  /callback**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
    'number_from': "+1254658744",
    'number_to': "2818454250",
    'text': "good morning...", 
    'state': "send"/"received"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| number_from | true | |  
| number_to   | true | |  
| text        | true | |  
| state       | true | |  

###### output
``` json 

``` 

###HTTP REQUEST :  **GET  /last-10-history-list**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
    'user_id': "1",
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| user_id | true | |   

###### output
``` json 
{
    "results": [
        {
            "id": 43,
            "text": "forhad 88",
            "time": "2019-04-20T05:50:16.803321Z",
            "state": "send",
            "message_from": [
                "+19402209677"
            ],
            "message_to": [
                "+12816388201"
            ]
        },
        {
            "id": 42,
            "text": "forhad 88",
            "time": "2019-04-20T05:49:38.535695Z",
            "state": "send",
            "message_from": [
                "+19402209677"
            ],
            "message_to": [
                "+12816388201"
            ]
        }
    ],
    "count": 2
}
``` 

###HTTP REQUEST :  **GET  /single-history/<int:message_id>**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
    'message_id': "23",
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| message_id | true | |   

###### output
``` json 
{
    "id": 23,
    "text": "Send Message to common",
    "time": "2019-04-14T09:57:19.933174Z",
    "state": "send",
    "message_from": [
        "+12816388201"
    ],
    "message_to": [
        "+19402209677"
    ]
}
``` 

###HTTP REQUEST :  **POST  /change-callback-url**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
    'url': "http://books.agiliq.com",
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| user_id | true | |   

###### output
``` json 
{

}
``` 

###HTTP REQUEST :  **GET  /get-notifications**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
    'user_id': "2",
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| user_id | true | |   

###### output
``` json 
{
    "results": [
    {
        'id': 1, 
        'text': "text messages...", 
        'time': ""2019-01-14T19:40:16Z", 
        'state': "send"/"received", 
        'message_from': "+16979565623", 
        'message_to': "+16979568888"
    }
    ],
    "count": 1
}
``` 



###HTTP REQUEST :  **GET  /accountnumbers/<str:e164>/conversations/<str:number>**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| user_id | true | |   

###### output
``` json 
{
    "count": 4,
    "next": null,
    "limit": 20,
    "results": [
        {
            "id": 5,
            "text": "+19402209677 - Hello from the other world",
            "time": "2019-04-28T08:04:04.322817Z",
            "state": "send",
            "message_from": "+19402209677",
            "message_to": "+12816388201"
        },
        {
            "id": 4,
            "text": "1",
            "time": "2019-04-28T08:04:03.516873Z",
            "state": "send",
            "message_from": "+19402209677",
            "message_to": "+12816388201"
        },
        {
            "id": 2,
            "text": "+19402209677 - Hello Localhost",
            "time": "2019-04-28T08:02:30.467638Z",
            "state": "send",
            "message_from": "+19402209677",
            "message_to": "+12816388201"
        },
        {
            "id": 1,
            "text": "Hello Localhost",
            "time": "2019-04-28T08:02:29.549168Z",
            "state": "send",
            "message_from": "+19402209677",
            "message_to": "+12816388201"
        }
    ],
    "previous": null
}
``` 

###HTTP REQUEST :  **POST  /upload**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "file": "image.jpg"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| file | true | |   

###### output
``` json 
{
    "file": "http://127.0.0.1:8002/media/file/d7b0ea0d-ff42-4aab-b8e6-a6d646292b65.png"
}
``` 

###HTTP REQUEST :  **GET  /single-external-number/<str:number>**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "number": "+12816388201"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| number      | true | |   

###### output
``` json 
{
    "next": null,
    "previous": null,
    "count": 1,
    "limit": 20,
    "results": [
        {
            "id": 1,
            "source": "+13464040600",
            "e164": "+12818454250"
        }
    ]
}
``` 

###HTTP REQUEST :  **DELETE  /single-external-number/<str:number>**

###### header
```
{
   "Authorization":"Bearer fd303bef03c9a1e199041854d1230c50ebff0735"      
}
```
###### params

```json 
{    
     "number": "+12816388201"
}
```
| parameter | is required | comment |
| :---------: | :---: | :-----------: | :-------: | :----------- |
| number      | true | |   

###### output
``` json 

``` 