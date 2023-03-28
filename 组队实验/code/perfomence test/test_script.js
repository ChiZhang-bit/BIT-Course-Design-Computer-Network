import http from 'k6/http';
import { check, sleep } from 'k6';

//options.stages 控制并发
//在执行脚本前30s内，虚拟用户增长至100
//在第30s-1m30s，虚拟用户减少至50
//最后30s，虚拟用户减少至0

export let options = {
  stages: [
    { duration: '30s', target: 100 },
    { duration: '1m30s', target: 50 },
    { duration: '30s', target: 0 },
  ],
};

export default function () {
  let res = http.get('192.168.56.1:8888');
  check(res, { 'status was 200': (r) => r.status == 200 });
  sleep(1);
}