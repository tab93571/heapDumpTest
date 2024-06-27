package org.kevin.demogcmetric;

import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class DemoGcMetricApplication implements CommandLineRunner {

  public static void main(String[] args) {
    SpringApplication.run(DemoGcMetricApplication.class, args);
  }

  @Override
  public void run(String... args) {
    System.out.println("ecs v1.2...");
  }
}


