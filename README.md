# P5 - Kafka (Bitcoin Tracker en tiempo real)

## Tarea a Realizar

* Crear un visualizador para la evolución del precio de bitcoin y el hash rate en ‘tiempo
real’ (streaming)
* Se actualizará su cotización en Dólares (USD) y el hash rate cada segundo
* Se mostrará en una gráfica con la evolución, con hasta 10000 medidas que se irán
actualizando

![image](https://github.com/GD-G10-2324/P5/assets/96234741/8317f506-daec-4c7c-ac98-603ea31d37fb)

## Pistas

Conocer el precio de Bitcoin
* Hay multitud de API REST para consultar
* Se proponen estas:
  - https://api.coindesk.com/v1/bpi/currentprice.json
  - https://api.blockchain.info/stats
* Los datos los devuelve en JSON → habría que tratar los datos antes del envío a Kafka
* Para representar gráficas en Java
  - Hay muchas alternativas
  - Se propone como ejemplo JFreeChart:
    * https://github.com/jfree/jfreechart
  - Ejemplo concreto de un gráfico para serie temporal:
    * https://github.com/anilbharadia/jFreeChart-Examples/blob/master/src/TimeSeriesDemo1.java
* Se tendrá que usar un gráfico con dos ejes diferentes
* Se podría tener que usar programación multihilo
* Se sugiere el uso de maven para gestionar todas las dependencias necesarias:
  - Kafka-clients
  - com.squareup.okhttp3
  - json
  - Jfreechart
  - …
* Se puede utilizar otro lenguaje de programación para implementar los productores y consumidores Kafka, así como el gráfico (por ejemplo, Python)
