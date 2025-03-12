# rase demove


## setup

```
  cp .env.development .env
  # and  add your RASA_PRO_LICENSE
```

### init project

```
docker run -v ./:/app \
            -e RASA_PRO_LICENSE=${RASA_PRO_LICENSE} \
            rasa/rasa-pro:3.11.3 \
            init --template tutorial --no-prompt

```

## train and inspect

```
docker run -v ./:/app \
            -e RASA_PRO_LICENSE=${RASA_PRO_LICENSE} \
            rasa/rasa-pro:3.11.3 \
            train

# inspect
docker run -v ./:/app \
            -p 5005:5005 \
            -e RASA_PRO_LICENSE=${RASA_PRO_LICENSE} \
            rasa/rasa-pro:3.11.3 \
            inspect
```

now you can visit http://localhost:5005
