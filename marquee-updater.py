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

                # See if our message starts with ###
                # This is unique to how we send "artist - title" metadata
                if(message.startswith('###')):
                    # Remove that initial identifier
                    message = message.lstrip('###')
                    # Split it
                    messageList = message.split('###')
                    # Validate we have six items
                    if(len(messageList = 6)):
                        firstColor = messageList[0]
                        firstMessage = messageList[1]
                        secondColor = messageList[2]
                        secondMessage = messageList[3]
                        thirdColor = messageList[4]
                        thirdMessage = messageList[5]

                        display_msg = alphasign.Text("%s%s%s%s%s%s%s%s%s" % (firstColor, font, firstMessage,
                                                    secondColor, font, secondMessage,
                                                    thirdColor, font, thirdMessage),
                                                    label="A",
                                                    mode=mode)
                else:
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
                #else:
                #    print("Display message has not changed. Skipping write...")

                if(rows.arraysize > 1):
                    time.sleep(sleepBetweenMessages)
                timeout = 0
            if(rows.arraysize > 1):
                time.sleep(sleepBetweenMessages)
            else:
                time.sleep(1)

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
