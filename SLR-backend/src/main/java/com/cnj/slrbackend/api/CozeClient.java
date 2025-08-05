package com.cnj.slrbackend.api;

import com.alibaba.dashscope.aigc.generation.GenerationResult;
import com.alibaba.dashscope.exception.ApiException;
import com.alibaba.dashscope.exception.InputRequiredException;
import com.alibaba.dashscope.exception.NoApiKeyException;
import com.alibaba.dashscope.utils.JsonUtils;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;

import java.net.HttpURLConnection;
import java.net.URL;
import java.io.OutputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.HashMap;
import java.util.Map;

public class CozeClient {
    private static final String API_URL = "https://api.coze.cn/open_api/v2/chat";

    public static String sendRequest(String botId, String token, String query) {
        try {
            // 1. 创建连接
            URL url = new URL(API_URL);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");

            // 2. 设置请求头
            conn.setRequestProperty("Authorization", "Bearer " + token);
            conn.setRequestProperty("Content-Type", "application/json");

            // 3. 构建请求体，推荐用Map+Jackson自动生成JSON
            Map<String, Object> body = new HashMap<>();
            body.put("bot_id", botId);
            body.put("user", "java_client_001");
            body.put("query", query);  // 这里 query 里有引号/大括号都没问题
            body.put("stream", false);
            body.put("disable_knowledge_recall", true);

            ObjectMapper mapper = new ObjectMapper();
            String jsonInput = mapper.writeValueAsString(body);

            // 4. 发送请求
            conn.setDoOutput(true);
            try (OutputStream os = conn.getOutputStream()) {
                os.write(jsonInput.getBytes());
                os.flush();
            }

            // 5. 解析响应
            if (conn.getResponseCode() == 200) {
                StringBuilder response = new StringBuilder();
                try (BufferedReader br = new BufferedReader(
                        new InputStreamReader(conn.getInputStream()))) {
                    String line;
                    while ((line = br.readLine()) != null) {
                        response.append(line);
                    }
                }
                return response.toString();
            } else {
                // 读取错误信息
                StringBuilder error = new StringBuilder();
                try (BufferedReader br = new BufferedReader(
                        new InputStreamReader(conn.getErrorStream()))) {
                    String line;
                    while ((line = br.readLine()) != null) {
                        error.append(line);
                    }
                }
                System.err.println("Error response: " + error);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return null;
    }

    public static void main(String[] args) {
    try {
        String botId = "7522844451316940826";
        String token = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx";
        String query = "练习目标是团结，算法判断结果是{ \"filename\": \"5678553293fc4e8da3b49fec9bab250a.mp4\", \"index\": 64, \"results\": [ [\"团结\", \"93.914%\"], ... ] }请求指导";
//        String query ="团结的手语怎么做";
        String result = sendRequest(botId, token, query);
        System.out.println(JsonUtils.toJson(result));
    }catch (Exception e)
    {
        System.out.println(e);
    }
    }

}