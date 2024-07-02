package org.kevin.demogcmetric;

import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class ApiController {

  List<byte[]> list = new ArrayList<>();
  String randomId = UUID.randomUUID().toString();

  @GetMapping
  public String hello() {
    System.out.println("hello world: " + randomId);
    return "hello world: " + randomId;
  }

  @GetMapping("memory")
  public String outOfMemory(@RequestParam("count") Integer count) {
    System.out.println("millisecond: " + count);
    for (int i = 0; i < count; i++) {
      byte[] b = new byte[1024 * 1024];
      list.add(b);
      System.out.printf("目前以使用%s mb%n", list.size());
    }
    return String.format("目前以使用%s mb", list.size());
  }

  @GetMapping("cleanMemory")
  public String cleanMemory() {
    list = new ArrayList<>();
    return String.format("目前以使用%s mb", list.size());
  }

  @GetMapping("cpu")
  public void cpu() {
    System.out.println("start cpu test...");
    int num = 0;
    long start = System.currentTimeMillis() / 1000;
    while (true) {
      num++;
      if (Integer.MAX_VALUE == num) {
        System.out.println("reset");
        num = 0;
      }
      if ((System.currentTimeMillis() / 1000) - start > 180) {
        System.out.println("end...");
        return;
      }
    }
  }
}
