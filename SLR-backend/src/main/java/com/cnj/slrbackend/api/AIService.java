package com.cnj.slrbackend.api;

import com.fasterxml.jackson.databind.JsonNode;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;
import reactor.core.publisher.Mono;

import java.util.Map;

@Service
public class AIService {
    private final WebClient webClient;
    private final String botId;

    public AIService(WebClient cozeWebClient, @Value("${coze.bot-id}") String botId) {
        this.webClient = cozeWebClient;
        this.botId = botId;
    }

    public Mono<String> chat(String message) {
        return webClient.post()
                .bodyValue(Map.of(
                        "bot_id", botId,
                        "user", "spring_client",
                        "query", message
                ))
                .retrieve()
                .bodyToMono(JsonNode.class)
                .map(node -> {
                    JsonNode messages = node.get("messages");
                    if (messages != null && messages.isArray()) {
                        for (JsonNode msg : messages) {
                            // 只要AI最终生成内容，不要插件/召回/中间态
                            if ("assistant".equals(msg.path("role").asText())
                                    && "answer".equals(msg.path("type").asText())
                                    && msg.has("content")
                                    && !msg.get("content").asText().isBlank()) {
                                return msg.get("content").asText();
                            }
                        }
                        // 没有最终内容就fallback
                        return messages.get(0).get("content").asText();
                    }
                    return "";
                });
//                .retrieve()
//                .bodyToMono(JsonNode.class)
//                .map(node -> node.get("messages").get(0).get("content").asText());
    }


    // 使用WebFlux处理流式响应
    public Flux<String> streamChat(String message) {
        return webClient.post()
                .bodyValue(Map.of(
                        "bot_id", botId,
                        "stream", true,
                        "query", message
                ))
                .accept(MediaType.TEXT_EVENT_STREAM)
                .retrieve()
                .bodyToFlux(String.class)
                .filter(data -> data.startsWith("data:"))
                .map(data -> data.substring(5).trim());
    }

}