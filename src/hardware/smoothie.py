class Smoothie(object):
    def __init__(self, uartdev):
        """
        Args:
            uartdev (UART)
        """
        self._uart = uartdev

    def connect(self, retry_times):
        """
        Args:
            retry_times (int): retry times for connect to Smoothie board
        """
        for _ in range(retry_times):
            self._uart.open()
            if self.recv() == 'Smoothie' and self.recv() == 'ok':
                return True

            self.send('G')
            if self.recv() != 'ok':
                self._uart.close()
                continue

            return True

    def disconnect(self):
        self._uart.close()

    def send(self, data):
        """
        Args:
            data (str): Gcode to write
        """
        self._uart.writeline(data)

    def recv(self):
        return self._uart.readlien().strip()
