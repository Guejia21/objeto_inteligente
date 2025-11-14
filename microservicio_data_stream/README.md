Para instalar micropython en linux debe seguirse la guia:
https://docs.micropython.org/en/latest/develop/gettingstarted.html
Se puede crear un enlace simbolico para usar micropython como un comando nativo, de esta forma:

sudo ln -s <"rutamicropython">/micropython /usr/local/bin/micropython

# Nota importante
Para la ejecución con la rasberry se recomienda hacerlo con python3, por lo tanto se deberán hacer cambios respecto a las librerias, por ejemplo, en vez de ujson (para micropython) usar json