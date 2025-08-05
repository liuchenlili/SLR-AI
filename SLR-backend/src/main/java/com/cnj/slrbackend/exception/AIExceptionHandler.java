package com.cnj.slrbackend.exception;

import io.swagger.v3.oas.annotations.Hidden;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.reactive.function.client.WebClientResponseException;

import static org.springframework.http.HttpStatus.TOO_MANY_REQUESTS;
import static org.springframework.http.HttpStatus.UNAUTHORIZED;
@Hidden
@ControllerAdvice
public class AIExceptionHandler {

    @ExceptionHandler(WebClientResponseException.class)
    public ResponseEntity<String> handleCozeError(WebClientResponseException ex) {
        return switch (ex.getStatusCode()) {
            case UNAUTHORIZED -> ResponseEntity.status(401).body("无效的访问令牌");
            case TOO_MANY_REQUESTS -> ResponseEntity.status(429).body("请求超限");
            default -> ResponseEntity.status(500).body("AI服务异常");
        };
    }
}
