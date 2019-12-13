// wink.c
// LED blink test
// hardware: LED with resistor shall be connected to GPIOxx
// compile: cc wink.c -o wink
// execute: sudo ./wink xx

#include <stdio.h>
#include <string.h>
#include <fcntl.h>
#include <errno.h>

//  HACK: 要リファクタリング 
int main (int argc, char *argv[]){
  char buf[40];
  int port;
  int fd;
  int ret;

  port = atoi(argv[1]);

  // ./wink xx 
  //エラー処理　xxのGPIOが設定されていない
  if(port == 0){
    fprintf(stderr, "GPIO指定なし.\n");
    return -1;
  }

  // enable port

  // GPIOセットアップ
  sprintf(buf, "/sys/class/gpio/gpio%d/direction", port);
  fd = open(buf, O_WRONLY);
  write(fd, "out", 3);
  close(fd);

  // ポート開放
  sprintf(buf, "/sys/class/gpio/gpio%d/value", port);
  fd = open(buf, O_WRONLY);

  //printf("%s\n", buf);
  //return 0;

//  for(int i = 0; i < 10; i++){
//  printf("count%d: on", i);

    //lseek(fd, 0, SEEK_SET);
    //赤外線送信　ON
    write(fd, "1", 2);
    sleep(0.1);

    //lseek(fd, 0, SEEK_SET);
    //赤外線送信　OFF
    write(fd, "0", 2);
    sleep(0.1);

//  }

  // ポートを無効にする処理
  fd = open("/sys/class/gpio/unexport", O_WRONLY);
  sprintf(buf, "%d", port);
  write(fd, buf, strlen(buf));
  close(fd);

  return 0;
} 