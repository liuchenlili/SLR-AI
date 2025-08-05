package com.cnj.slrbackend.config;


import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.util.Map;

@Configuration
public class CozeConfig {

    @Value("${coze.bot-id}")
    private String botId;

    @Value("${coze.access-token}")
    private String token;

    @Bean
    public WebClient cozeWebClient() {
        return WebClient.builder()
                .baseUrl("https://api.coze.cn/open_api/v2/chat")
                .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + token)
                .build();
    }
}



