package org.kevin.demogcmetric;

import jakarta.servlet.http.HttpServletRequest;
import java.net.InetAddress;
import java.net.UnknownHostException;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class DemoGcMetricApplication implements CommandLineRunner {

  public static void main(String[] args) {
    SpringApplication.run(DemoGcMetricApplication.class, args);
  }

  @Override
  public void run(String... args) throws Exception {
    System.out.println("ecs v1.0...");
  }
}

@RestController
class MyController {

  @GetMapping
  public String hello() {
    System.out.println("hello world");
    return "hello world: ";
  }

  @GetMapping("m")
  public String outOfMemory(@RequestParam("millisecond") String millisecond) throws InterruptedException {
    if (millisecond == null) {
      millisecond = "100";
    }
    List<byte[]> list = new ArrayList<>();
    System.out.println("millisecond: " + millisecond);
    while (true) {
      byte[] b = new byte[1024 * 1024 * 10];
      list.add(b);
      Thread.sleep(Long.parseLong(millisecond));
      System.out.println(list.size() + "0 mb");
      if (list.size() > 44) {
        System.out.println("sleep 30s...");
        Thread.sleep(30000);
      }
    }
  }

  @GetMapping("c")
  public void cpu() {
    System.out.println("start...");
    int num = 0;
    long start = System.currentTimeMillis() / 1000;
    while (true) {
      num++;
      if (Integer.MAX_VALUE == num) {
        System.out.println("reset");
        num = 0;
      }
      if ((System.currentTimeMillis() / 1000) - start > 60) {
        System.out.println("end...");
        return;
      }
    }
  }

}
