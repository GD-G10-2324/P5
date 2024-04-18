import threading
import time
import requests
from kafka import KafkaConsumer, KafkaProducer
import matplotlib.dates as mdates
import matplotlib.ticker as mtick
from collections import deque
from datetime import datetime as dt
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation
import logging

# Constantes globales
TOPIC_NAME = 'HelloKafka'
LINK_A = 'https://api.coindesk.com/v1/bpi/currentprice.json'
LINK_B = 'https://api.blockchain.info/stats'
MAX_ITEMS = 10000
INTERVAL = 1000
DEGREES = 60
bootstrap_servers = ['localhost:9092']
STYLE = 'seaborn-v0_8-pastel'

# Configuración logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(threadName)s %(levelname)s %(message)s', filename=str(
    dt.now().replace(microsecond=0)).replace(':', '-').replace(' ', '-')+'.log', filemode='a')

# Clase productora de mensajes Kafka, para valores de Bitcoin y Hash-Rate
class BitcoinGetter(threading.Thread):
    def __init__(self):
        self.server = bootstrap_servers[0]
        self.topic = TOPIC_NAME
        self.producer = KafkaProducer(bootstrap_servers=self.server)

    def produce(self):
        try:
            while 1:
                response_a = requests.get(LINK_A)
                response_a.raise_for_status()
                x = response_a.json()['bpi']['USD']['rate_float']
                response_b = requests.get(LINK_B)
                response_b.raise_for_status()
                y = response_b.json()['hash_rate']
                z = str(x) + ':' + str(y)
                logging.info(f'[KP] {z}')
                self.producer.send(TOPIC_NAME, str(z).encode('utf-8'))
                self.producer.flush()
                time.sleep(0.0001)
        except Exception as e:
            logging.warning(e)
            exit(-1)

# Clase consumidora de mensajes Kafka, con gráfica animada incluida
class Plotter(threading.Thread):
    def __init__(self):
        self.bootstrap_servers = bootstrap_servers
        self.topic = TOPIC_NAME
        self.consumer = KafkaConsumer(
            self.topic, bootstrap_servers=self.bootstrap_servers)
        self.max_items = MAX_ITEMS
        self.bitcoin = deque([], self.max_items)
        self.hash_rate = deque([], self.max_items)
        self.times = deque([], self.max_items)
        self.style = STYLE
        self.fig = plt.figure(num='Bitcoin y Hash-Rate G10', figsize=(11, 6))
        self.config_plot()

    def config_plot(self):
        plt.style.use(STYLE)
        self.ax1 = self.fig.add_subplot(111)
        self.ax1.set_title("Evolución del precio de bitcoin y el hash rate")
        self.ax1.set_xlabel("Hora")
        self.ax1.set_ylabel("Bitcoin (USD)")
        self.ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax1.tick_params(axis='x', labelrotation=DEGREES)
        self.ax2 = self.ax1.twinx()
        self.ax2.set_ylabel("Hash-Rate")
        self.ax2.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2e'))
        self.line1, = self.ax1.plot_date(
            self.times, self.bitcoin, color='tab:blue', linestyle='-', marker='', label='Valor Bitcoin')
        self.line2, = self.ax2.plot_date(
            self.times, self.hash_rate, color='tab:red', linestyle='-', marker='', label='Hash-Rate')
        both_lines = [self.line1, self.line2]
        my_labels = [l.get_label() for l in both_lines]
        self.fig.legend(both_lines, my_labels, loc='upper right')

    def get_actual_time(self):
        return dt.now().replace(microsecond=0)

    def update(self, i):
        for _, messages in self.consumer.poll(timeout_ms=100).items():
            for message in messages:
                values = message.value.decode('utf-8').split(':')
                date = self.get_actual_time()
                if date not in self.times:
                    self.times.append(date)
                    self.bitcoin.append(float(values[0]))
                    self.hash_rate.append(float(values[1]))
                    logging.info(f'[MPLIB] {values[0]}, {values[1]}, {date}')
                    self.line1.set_data(self.times, self.bitcoin)
                    self.line2.set_data(self.times, self.hash_rate)
                    self.ax1.relim()
                    self.ax2.relim()
                    self.ax1.autoscale_view()
                    self.ax2.autoscale_view()
                return self.line1, self.line2

    def start_animation(self):
        ani = FuncAnimation(self.fig, self.update,
                            interval=INTERVAL, cache_frame_data=False)
        plt.show()

# Gestor de hilos
class KafkaThreadManager:
    def __init__(self):
        self.producer = BitcoinGetter()
        self.plotter = Plotter()

    def run(self):
        try:
            producer_thread = threading.Thread(
                target=self.producer.produce, daemon=True)
            producer_thread.start()
            self.plotter.start_animation()
        except KeyboardInterrupt as e:
            producer_thread.join()
            logging.warning(e)
            exit(0)


def main():
    kafka_thread_manager = KafkaThreadManager()
    kafka_thread_manager.run()
    logging.info('Fin del programa')


if __name__ == "__main__":
    main()
