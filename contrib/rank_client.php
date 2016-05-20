<?php

$params = array();
$params["algo"] = "legacy";
$cars = array();
for ($i=0; $i<500; $i++) $cars[] = rand()%10000;
$params["car_list"] = $cars;
$dis = array();
for ($i=0; $i<500; $i++) $dis[] = rand()%10;
$params["distance"] = $dis;
$params["user_id"] = 20145;
$data = json_encode($params);

var_dump($data);

$url = "http://127.0.0.1:20164/legacy";

$c = curl_init($url);
//curl_setopt($c, CURLOPT_URL, $url);
//curl_setopt($c, CURLOPT_PORT, 20164);
curl_setopt($c, CURLOPT_POST, true);
curl_setopt($c, CURLOPT_POSTFIELDS, $data);
curl_setopt($c, CURLOPT_RETURNTRANSFER, true);
curl_setopt($c, CURLOPT_HTTPHEADER, array('Expect:'));
curl_setopt($c, CURLOPT_HEADER, false);
curl_setopt($c, CURLOPT_TIMEOUT_MS, 2000);
curl_setopt($c, CURLOPT_NOSIGNAL, true);

$before = microtime(true);
$ret = curl_exec($c);

$after = microtime(true);
var_dump($ret);
echo ($after-$before) . " secs\n";

curl_close($c);
