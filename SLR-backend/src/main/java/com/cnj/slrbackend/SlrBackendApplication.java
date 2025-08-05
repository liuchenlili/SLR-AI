package com.cnj.slrbackend;

import org.mybatis.spring.annotation.MapperScan;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
@MapperScan("com.cnj.slrbackend.mapper")
public class SlrBackendApplication {

	public static void main(String[] args) {
		SpringApplication.run(SlrBackendApplication.class, args);
	}

}
