#!/usr/bin/env python

import os
import alphasign
import sqlite3
import serial
import time

def display():
    sleepBetweenMessages = 20
    conn = sqlite3.connect('/app/db/marquee_messages.db')
    c = conn.cursor()
    timeout = 0
    previous_display_msg = " "

    while True:
        try:
            sign = alphasign.Serial(device='/dev/ttyUSB0')
            sign.connect()

            rows = c.execute('select text, color_name, font_name, mode_name ' + \
                'from messages ' + \
                'left join colors on colors.color_id = messages.color_id ' + \
                'left join fonts on fonts.font_id = messages.font_id ' + \
                'left join modes on modes.mode_id = messages.mode_id ' + \
                'order by message_id desc')
            for row in rows:
                message = str(row[0])
                color = getattr(alphasign.colors, str(row[1]))
                mode = getattr(alphasign.modes, str(row[3]))
                font = getattr(alphasign.charsets, str(row[2]))

                display_msg = alphasign.Text("%s%s%s" % (color, font, message),
                                                label="A",
                                                mode=mode)

                if(str(display_msg) != str(previous_display_msg)):
                    try:
                        print("Writing message: %s, color: %s, font: %s, mode: %s" % (message, color, font, mode))
                        sign.write(display_msg)
                        previous_display_msg = display_msg
                    except Exception as e:
                        print("Failed to write to sign: " + str(e))
                        continue #not working correctly
                else:
                    print("Display message has not changed. Skipping write...")

                time.sleep(sleepBetweenMessages)
                timeout = 0
            time.sleep(sleepBetweenMessages)

        except Exception as e:
            print("General Exception: " + str(e))
            if timeout > 4:
                timeout = 0
                time.sleep(sleepBetweenMessages)
            else:
                time.sleep(timeout)
                timeout += 1
                print("Timeout: " + str(timeout))


if __name__ == '__main__':
    display()
