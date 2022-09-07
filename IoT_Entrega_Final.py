#! /usr/bin/python2
#Librerias
import RPi.GPIO as GPIO
import Adafruit_DHT
import thingspeak
import time
import sys
from hx711 import HX711
import paho.mqtt.publish as publish
import paho.mqtt.publish as publish
from datetime import date,datetime
today = date.today()
Dia=today.weekday() # Lunes = 0 -> Domingo = 6
Today = datetime.now()
Hora=Today.strftime("%H")
Minutos=Today.strftime('%M')
#print(Hora, ':',Minutos)
#Funciones
def AngleToDuty(ang):
  return float(pos)/10.+5.

channel_id = "1693330"
write_key = "9GR3X4WZCVENONES"

referenceUnit = 11
T_Sleep= 20 #Tiempo entre dato y dato (decimas de segundos)
Conteo=0    #Delta entre la medicion del sensor infrarojo y los otros 2
PersonaIR1=False # Variable para que no se spamee el sensor infra rojo
PersonaIR=False
PersonasDetectadas=0
PersonasDetectadasn=0
SillaOcupada=False


sensor = Adafruit_DHT.DHT11
pint = 4 # Pin sensor temperatura = pin 4

GPIO.setmode(GPIO.BCM)
pinin = 17
pininn= 18
GPIO.setup (pinin, GPIO.IN)
input = GPIO.input(pinin)
GPIO.setup (pininn, GPIO.IN)
input = GPIO.input(pininn)

hx = HX711(5, 6)

hx.set_reading_format("MSB", "MSB")
hx.set_reference_unit(referenceUnit)
hx.reset()
hx.tare()

channel=thingspeak.Channel(id=channel_id, api_key=write_key)
EnvioXDia=False
servoPin=25
GPIO.setmode(GPIO.BCM)
GPIO.setup(servoPin,GPIO.OUT)
pwm=GPIO.PWM(servoPin,100)
#setup sweep parameters
depart =90 #Angulo Salida
on=180 #Angulo Prender Ventilador
off=0  #Angulo Apagar Ventilador
DELAY=0.02  #Delay Servo
incStep=3  #Tasa cambio angulo servo
pos=depart #Angulo Inincial
VentEnc=False #Ventilador Encendido
VentManual=False#Ventilador Manual
pwm.start(AngleToDuty(pos))
if __name__ == '__main__':
 while True:
     #sensor temperatura
     if (Conteo==T_Sleep):
         Conteo=0
         if(int(Dia)!=6) and (int(Hora)==23) and (int(Minutos)>=50) and (EnvioXDia==False):
             EnvioXDia=True #Ya envio Clientes Hoy
             channel.update({'field6':Dia ,'field7':PersonasDetectadas})
             PersonasDetectadas=0
             PersonasDetectadasn=0
             
         elif (int(Hora)==0) and (int(Minutos)<=10) and (EnvioXDia==True):
             EnvioXDia=False
             today = date.today()
             Dia=today.weekday() # Lunes = o -> Domingo = 6
         else:             
             Today = datetime.now()
             Hora=Today.strftime("%H")
             Minutos=Today.strftime('%M')
        #%% Obtencion temperatura y humedad
         humedad, temperatura = Adafruit_DHT.read_retry(sensor, pint)
        #Muestra en pantalla la temperatura en °C, °F y la humedad del aire    
         print ("{:.1f} C°  humedad: {}%".format(temperatura, humedad))
         if VentManual==False:
             
             if (VentEnc==False) and (temperatura >= 20):
                 
                 VentEnc=True
                 #pwm.start(AngleToDuty(pos)) #star pwm
                 nbRun=0.1
                 for pos in range(depart,on,incStep):
                     duty=AngleToDuty(pos)
                     pwm.ChangeDutyCycle(duty)
                     time.sleep(DELAY)
                 for pos in range(on,depart,-incStep):
                     duty=AngleToDuty(pos)
                     pwm.ChangeDutyCycle(duty)
                     time.sleep(DELAY)
                 #pwm.stop() #stop sending value to output
             elif (VentEnc==True) and (temperatura <= 18):    
                 VentEnc=False
                 #pwm.start(AngleToDuty(pos)) #star pwm
                 nbRun=0.1
                 for pos in range(depart,off,-incStep):
                     duty=AngleToDuty(pos)
                     pwm.ChangeDutyCycle(duty)
                     time.sleep(DELAY)
                 for pos in range(off,depart,incStep):
                     duty=AngleToDuty(pos)
                     pwm.ChangeDutyCycle(duty)
                     time.sleep(DELAY)
                 #pwm.stop() #stop sending value to output
             #GPIO.cleanup()
     #sensor infrarojo
     if (not (GPIO.input(pinin)) and (PersonaIR==False)):
        
        PersonasDetectadas+=1
        PersonaIR=True
        print("Personas detectadas totales = " + str(PersonasDetectadas))
     elif(PersonaIR==True and (not (GPIO.input(pinin)))):
        pass
    #Si el sensor justo deja de detectar a alguien 
     else:
        PersonaIR=False
        
    #Espera 10 segundo para tomar el proximo dato

     if (not (GPIO.input(pininn)) and (PersonaIR1==False)):
        PersonasDetectadasn+=1
        PersonaIR1=True
        print("Personas salientes totales = " + str(PersonasDetectadasn))
        
     elif(PersonaIR1==True and (not (GPIO.input(pininn)))):
        pass
    #Si el sensor justo deja de detectar a alguien 
     else:
        PersonaIR1=False
        
     #celda de carga
      
     try:
        val=hx.get_weight(5)

        if(val<25000):
           valor=0
           if(SillaOcupada==True):
               print(valor)
           SillaOcupada=False
        else:
           valor=1
           if(SillaOcupada==False):
               print(valor)
           SillaOcupada=True
        time.sleep(0.01)

     except (KeyboardInterrupt, SystemExit):
        cleanAndExit()
     try:
      channel.update({'field1':temperatura ,'field2':abs(PersonasDetectadas-PersonasDetectadasn) ,
                      'field3': PersonasDetectadas,
                      'field4': PersonasDetectadasn,'field5':valor})
      #print("datos enviados")
     except:
      print("Error enviando datos")
      
     time.sleep(0.5)
     Conteo+=1
 