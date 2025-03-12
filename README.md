# rase demove


## setup

```
  cp .env.development .env
  # and  add your RASA_PRO_LICENSE
```

### init project
docker run -v ./:/app \
            -e RASA_PRO_LICENSE=${RASA_PRO_LICENSE} \
            rasa/rasa-pro:3.11.3 \
            init --template tutorial --no-prompt
