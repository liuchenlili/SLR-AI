package com.cnj.slrbackend.controller;

import com.cnj.slrbackend.utils.MultipartInputStreamFileResource;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.io.IOException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.*;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.*;

@RestController
@RequestMapping("/python")
public class PredictionController {

    // 同级目录
    private final WebClient webClient;
    private final String WEIGHT_BASE = "SLR-S/weight/";
    private final String LOG_BASE = "SLR-S/logs/";

    @Autowired
    public PredictionController(WebClient webClient) {
        this.webClient = webClient;
    }

    /**
     * 1️⃣ 预测接口：调用 FastAPI
     */
    @PostMapping("/predict")
    public Mono<String> predict(
            @RequestParam(value = "file", required = false) MultipartFile file,
            @RequestParam("model") String model,
            @RequestParam("weight") String weight,
            @RequestParam("videoStyle") String videoStyle,
            @RequestParam("centercrop") boolean centercrop,
            @RequestParam(value = "video_path", required = false) String videoPath // 新增
    ) throws IOException {

        MultiValueMap<String, Object> formData = new LinkedMultiValueMap<>();
        formData.add("model", model);
        formData.add("weight", weight);
        formData.add("video_style", videoStyle);
        formData.add("centercrop", String.valueOf(centercrop));
        if (videoPath != null && !videoPath.isEmpty()) {
            formData.add("video_path", videoPath); // 测试集模式
        }
        if (file != null && !file.isEmpty()) {
            Resource fileResource = new MultipartInputStreamFileResource(file.getInputStream(), file.getOriginalFilename());
            formData.add("file", fileResource); // 上传/录制模式
        }

        return webClient.post()
                .uri("/predict/video")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .bodyValue(formData)
                .retrieve()
                .bodyToMono(String.class);
    }

    /**
     * 2️⃣ 权重文件列表
     */
    @GetMapping("/weights")
    public ResponseEntity<List<String>> getWeights(@RequestParam String model) {
        File weightDir = new File(WEIGHT_BASE + model);
        String[] files = weightDir.list((dir, name) -> name.endsWith(".pth") || name.endsWith(".pt"));
        if (files != null) {
            Arrays.sort(files, Comparator.reverseOrder());
            return ResponseEntity.ok(Arrays.asList(files));
        }
        return ResponseEntity.ok(Collections.emptyList());
    }

    /**
     * 3️⃣ 获取准确率曲线 CSV
     */
    @GetMapping("/metrics/acc")
    public ResponseEntity<List<String>> getAccCurve(@RequestParam String model) throws IOException {
        File csvFile = new File(LOG_BASE + "csv/" + model + "_acc.csv");
        List<String> lines = Files.readAllLines(csvFile.toPath(), StandardCharsets.UTF_8);
        return ResponseEntity.ok(lines);
    }

    /**
     * 4️⃣ 获取损失曲线 CSV
     */
    @GetMapping("/metrics/loss")
    public ResponseEntity<List<String>> getLossCurve(@RequestParam String model) throws IOException {
        File csvFile = new File(LOG_BASE + "csv/" + model + "_loss.csv");
        List<String> lines = Files.readAllLines(csvFile.toPath(), StandardCharsets.UTF_8);
        return ResponseEntity.ok(lines);
    }

    /**
     * 5️⃣ 网络结构 SVG
     */
    @GetMapping("/net/graph")
    public ResponseEntity<String> getNetworkGraph(@RequestParam String model) throws IOException {
        File svgFile = new File(LOG_BASE + "net/" + model + ".onnx.svg");
        String content = Files.readString(svgFile.toPath(), StandardCharsets.UTF_8);
        return ResponseEntity.ok(content);
    }

    /**
     * 6️⃣ 混淆矩阵 PNG（Base64编码）
     */
    @GetMapping("/metrics/confusion")
    public ResponseEntity<String> getConfusionMatrix(@RequestParam String model) throws IOException {
        File imageFile = new File(LOG_BASE + "confusion_matrix/" + model + "_confmat.png");
        byte[] bytes = Files.readAllBytes(imageFile.toPath());
        String base64 = Base64.getEncoder().encodeToString(bytes);
        return ResponseEntity.ok("data:image/png;base64," + base64);
    }
}

