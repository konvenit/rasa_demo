# rase demo

## setup

```
  cp .env.development .env
  # add your RASA_PRO_LICENSE to .env
```

### init project

```
docker run -v ./:/app \
            -e RASA_PRO_LICENSE=${RASA_PRO_LICENSE} \
            rasa/rasa-pro:3.11.3 \
            init --template tutorial --no-prompt

```

### train

```
docker run -v ./:/app \
            -e RASA_PRO_LICENSE=${RASA_PRO_LICENSE} \
            rasa/rasa-pro:3.11.3 \
            train
```

###  inspect for debugging
docker run -v ./:/app \
            -p 5005:5005 \
            -e RASA_PRO_LICENSE=${RASA_PRO_LICENSE} \
            rasa/rasa-pro:3.11.3 \
            inspect
```

now you can visit http://localhost:5005

## run web gui

```
# maybe you have to train your models first. see train command

docker compose up

```

open http://localhost
