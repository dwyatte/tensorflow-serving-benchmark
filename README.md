# tensorflow-serving-benchmark
I couldn't find any benchmarks of [TensorFlow Serving](https://github.com/tensorflow/serving)
and wanted to know the throughput of the native gRPC client compared to a REST-based
client that forwards requests to the a gRPC client (which most people are likely
to use for external-facing services).

### Usage and Results
##### gRPC (async)
`docker-compose run grpc-benchmark`
<pre>
Creating tensorflowservingbenchmark_server_1 ... done

10000 requests (10 max concurrent)
<b>2487.13826442827 requests/second</b>
</pre>

##### WSGI (gunicorn/falcon, four workers, sync)
`docker-compose run wsgi-benchmark`
<pre>
Starting tensorflowservingbenchmark_server_1 ... done
Creating tensorflowservingbenchmark_wsgi-client_1 ... done
This is ApacheBench, Version 2.3 <$Revision: 1706008 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking wsgi-client (be patient)
...

Server Software:        gunicorn/19.7.1
Server Hostname:        wsgi-client
Server Port:            8000

Document Path:          /prediction
Document Length:        12 bytes

Concurrency Level:      10
Time taken for tests:   7.116 seconds
Complete requests:      10000
Failed requests:        0
Total transferred:      1790000 bytes
HTML transferred:       120000 bytes
<b>Requests per second:    1405.31 [#/sec] (mean)</b>
Time per request:       7.116 [ms] (mean)
Time per request:       0.712 [ms] (mean, across all concurrent requests)
Transfer rate:          245.66 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       1
Processing:     2    7  25.4      6     953
Waiting:        2    7  25.4      6     953
Total:          3    7  25.4      6     954

Percentage of the requests served within a certain time (ms)
  50%      6
  66%      7
  75%      7
  80%      7
  90%      8
  95%      8
  98%     10
  99%     11
 100%    954 (longest request)
 </pre>

##### Tornado (four workers, async)
`docker-compose run tornado-benchmark`
<pre>
Starting tensorflowservingbenchmark_server_1 ... done
Starting tensorflowservingbenchmark_tornado-client_1 ... done
This is ApacheBench, Version 2.3 <$Revision: 1706008 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking tornado-client (be patient)
...


Server Software:        TornadoServer/4.5.3
Server Hostname:        tornado-client
Server Port:            8001

Document Path:          /prediction
Document Length:        15 bytes

Concurrency Level:      10
Time taken for tests:   19.140 seconds
Complete requests:      10000
Failed requests:        0
Total transferred:      2100000 bytes
HTML transferred:       150000 bytes
<b>Requests per second:    522.47 [#/sec] (mean)</b>
Time per request:       19.140 [ms] (mean)
Time per request:       1.914 [ms] (mean, across all concurrent requests)
Transfer rate:          107.15 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.1      0       2
Processing:     3   19  15.2     17     447
Waiting:        3   19  15.2     16     447
Total:          3   19  15.2     17     447

Percentage of the requests served within a certain time (ms)
  50%     17
  66%     21
  75%     23
  80%     25
  90%     31
  95%     36
  98%     44
  99%     50
 100%    447 (longest request)
 </pre>
