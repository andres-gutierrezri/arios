import urllib
import datetime
import sys


def main():
    cant_arg = len(sys.argv)
    if cant_arg <= 1:
        print('#### Se debe pasar como argumento la url del endpoint para obtener los datos ###')
        exit(1)
    enviar_notificaciones_x_email(sys.argv[1])


def enviar_notificaciones_x_email(url):
    print("\nSe ejecuta el script para enviar notificaciones por email")
    print(datetime.datetime.now())

    sitio = urllib.urlopen(url)
    response = sitio.read()
    print(response)


if __name__ == '__main__':
    main()