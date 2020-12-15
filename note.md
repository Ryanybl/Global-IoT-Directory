## Procedure for adding a user attribute

### models.py
- In `class User(auth_db.Model, UserMixin)`, add database statements for the attribute.

- In `generate_user_info(self, user, scope)`, add
  
        if '<attribute_name>' in scope:
            user_info['<attribute_name>'] = <user.get_attribute()>

### utils.py
- Add the attribute as a new key to `auth_user_attributes` dictionary


### routes.py
- In `info_authorize`, store attribute value in `auth_user_attributes` 
  before `return redirect(url_for('auth.info_authorize'))`
  
### providers_config.py
`"client_kwargs": "scope"`


## Note for example oauth2 server
- Run `export AUTHLIB_INSECURE_TRANSPORT=1` in command line before starting the server.