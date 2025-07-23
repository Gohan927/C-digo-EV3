#!/usr/bin/env python3

from ev3dev2.motor import LargeMotor, OUTPUT_B, OUTPUT_C, SpeedPercent
from ev3dev2.sensor.lego import ColorSensor
from ev3dev2.sensor import INPUT_1, INPUT_2, INPUT_3
from time import sleep, time
from ev3dev2.sound import Sound

# Motores
motor_esq = LargeMotor(OUTPUT_B)
motor_dir = LargeMotor(OUTPUT_C)

# Sensores
sensor_esq = ColorSensor(INPUT_1)
sensor_meio = ColorSensor(INPUT_2)
sensor_dir = ColorSensor(INPUT_3)
sensor_meio.mode = 'COL-COLOR'

# Constantes
velocidade_base = 12
Kp = 1.4

# Inicializações
tempo_ultima_cor = time()
som = Sound()
cor_dir_anterior = 6  # começa como branco
cor_esq_anterior = 6  # começa como branco

try:
    while True:
        tempo_atual = time()

        # Verificação de cor a cada 0.2s
        if tempo_atual - tempo_ultima_cor >= 0.2:
            tempo_ultima_cor = tempo_atual

            # Troca sensores para modo cor
            sensor_esq.mode = 'COL-COLOR'
            sensor_dir.mode = 'COL-COLOR'
            sleep(0.01)

            cor_dir = sensor_dir.color 
            cor_esq = sensor_esq.color

            # Se algum dos sensores vê verde
            if cor_dir == 3 or cor_esq == 3:
                motor_esq.off()
                motor_dir.off()
                som.beep()
                sleep(0.1)

                # Lê novamente
                cor_dir2 = sensor_dir.color
                cor_esq2 = sensor_esq.color

                # Se os dois continuam vendo verde → gira 180°
                if (cor_dir2 == 3 or cor_dir2 == 2) and (cor_esq2 == 2 or cor_dir2 == 3):
                    #som.beep()
                    motor_esq.on_for_degrees(SpeedPercent(30), 420)
                    motor_dir.on_for_degrees(SpeedPercent(-30), 420)
                    sleep(0.2)
                    motor_esq.on(SpeedPercent(velocidade_base))
                    motor_dir.on(SpeedPercent(velocidade_base))
                    sleep(2)
                    continue

                # Se só a direita continua verde
                elif (cor_dir2 == 3 or cor_dir2 == 2) and cor_esq2 != 3:
                    if cor_dir_anterior == 6:  # branco
                        #som.beep()
                        motor_esq.on_for_degrees(SpeedPercent(20), 180)
                        motor_dir.on_for_degrees(SpeedPercent(-20), 180)
                        motor_esq.on(SpeedPercent(velocidade_base))
                        motor_dir.on(SpeedPercent(velocidade_base))
                        sleep(2)
                        continue
                    elif cor_dir_anterior == 1:  # preto
                        pass  # segue normalmente

                # Se só a esquerda continua verde
                elif (cor_esq2 == 3 or cor_esq2 == 2) and cor_dir2 != 3:
                    if cor_esq_anterior == 6:  # branco
                        #som.beep()
                        motor_dir.on_for_degrees(SpeedPercent(20), 180)
                        motor_esq.on_for_degrees(SpeedPercent(-20), 180)
                        motor_esq.on(SpeedPercent(velocidade_base))
                        motor_dir.on(SpeedPercent(velocidade_base))
                        sleep(2)
                        continue
                    elif cor_esq_anterior == 1:  # preto
                        pass  # segue normalmente

            # Atualiza cores anteriores
            cor_dir_anterior = cor_dir
            cor_esq_anterior = cor_esq

        else:  # PID para seguir a linha normalmente
            sensor_esq.mode = 'COL-REFLECT'
            sensor_dir.mode = 'COL-REFLECT'
            sleep(0.01)

            reflet_esq = sensor_esq.reflected_light_intensity
            reflet_dir = sensor_dir.reflected_light_intensity
            erro = reflet_dir - reflet_esq
            
            if abs(erro) < 15:
                erro = 0
            correcao = Kp * erro

            vel_esq = velocidade_base - correcao
            vel_dir = velocidade_base + correcao
            vel_esq = max(min(vel_esq, 100), -100)
            vel_dir = max(min(vel_dir, 100), -100)

            motor_esq.on(SpeedPercent(vel_esq))
            motor_dir.on(SpeedPercent(vel_dir))
            sleep(0.01)

        # Verifica fim de linha com sensor do meio (vermelho)
        cor_meio = sensor_meio.color
        if cor_meio == 5:
            motor_dir.off()
            motor_esq.off()
            som.beep()
            break

except KeyboardInterrupt:
    motor_esq.off()
    motor_dir.off()

