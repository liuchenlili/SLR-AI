package com.cnj.slrbackend.controller;

import com.baomidou.mybatisplus.extension.plugins.pagination.Page;
import com.cnj.slrbackend.api.AIService;
import com.cnj.slrbackend.common.BaseResponse;
import com.cnj.slrbackend.common.ResultUtils;
import com.cnj.slrbackend.exception.ErrorCode;
import com.cnj.slrbackend.exception.ThrowUtils;
import com.cnj.slrbackend.model.dto.predict.PracticeRecordQueryRequest;
import com.cnj.slrbackend.model.entity.PracticeRecord;
import com.cnj.slrbackend.model.entity.User;
import com.cnj.slrbackend.service.service.PracticeRecordService;
import com.cnj.slrbackend.service.service.UserService;
import com.cnj.slrbackend.utils.MultipartInputStreamFileResource;
import jakarta.servlet.http.HttpServletRequest;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;

import java.io.IOException;
import java.util.*;

@RestController
@RequestMapping("/practice")
public class PracticeController {
    private final WebClient webClient;
    private final AIService aiService;

    @jakarta.annotation.Resource
    private UserService userService;

    @jakarta.annotation.Resource
    private PracticeRecordService practiceRecordService;


    public PracticeController(WebClient webClient, AIService aiService) {
        this.webClient = webClient;
        this.aiService = aiService;
    }

    /**
     * 🎯 前端提交练习目标 + 视频，调用FastAPI预测+AI建议
     * 例如前端以
     *   targetText: "练习目标"
     *   file / video_path
     *   model, weight, videoStyle, centercrop
     * 发送 multipart/form-data
     */
    @PostMapping(value = "/fullPredict", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public Mono<Map<String, String>> fullPredict(
            @RequestParam("targetText") String targetText,
            @RequestParam(value = "file", required = false) MultipartFile file,
            @RequestParam("model") String model,
            @RequestParam("weight") String weight,
            @RequestParam("videoStyle") String videoStyle,
            @RequestParam("centercrop") boolean centercrop,
            @RequestParam(value = "video_path", required = false) String videoPath
    ) throws IOException {

        // 1️⃣ 组装表单
        MultiValueMap<String, Object> formData = new LinkedMultiValueMap<>();
        formData.add("model", model);
        formData.add("weight", weight);
        formData.add("video_style", videoStyle);
        formData.add("centercrop", String.valueOf(centercrop));

        if (videoPath != null && !videoPath.isEmpty()) {
            formData.add("video_path", videoPath);
        }

        if (file != null && !file.isEmpty()) {
            Resource resource = new MultipartInputStreamFileResource(
                    file.getInputStream(), file.getOriginalFilename());
            formData.add("file", resource);
        }

        // 2️⃣ 调用FastAPI微服务预测
        return webClient.post()
                .uri("/predict/video")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .bodyValue(formData)
                .retrieve()
                .bodyToMono(String.class)
                .flatMap(predictionJson -> {
                    // 3️⃣ 拼接 Prompt
                    String prompt = String.format(
                            "练习目标是：%s，算法预测结果是：%s，请给出详细教学建议。",
                            targetText,
                            predictionJson
                    );

                    // 4️⃣ 调用AI智能体
                    return aiService.chat(prompt)
                            .map(aiReply -> {
                                Map<String, String> result = Map.of(
                                        "prediction", predictionJson,
                                        "aiAdvice", aiReply
                                );
                                System.out.println("AI接口返回内容：" + result);
                                return result;
                            });

                });
    }
    /**
     * 新增一条练习记录（需登录）
     */
    @PostMapping("/add")
    public BaseResponse<Boolean> addPracticeRecord(@RequestBody PracticeRecord record, HttpServletRequest request) {
        // 获取当前登录用户
        User loginUser = userService.getLoginUser(request);
        record.setUserId(loginUser.getId());
        boolean result = practiceRecordService.saveRecord(record);
        return ResultUtils.success(result);
    }

    /**
     * 查询当前用户的全部练习记录
     */
    @GetMapping("/listMy")
    public BaseResponse<List<PracticeRecord>> listMyRecords(HttpServletRequest request) {
        User loginUser = userService.getLoginUser(request);
        List<PracticeRecord> list = practiceRecordService.listRecordsByUserId(loginUser.getId());
        return ResultUtils.success(list);
    }

    /**
     * 管理员/教师：按用户ID查询练习记录（可选）
     */
    @GetMapping("/listByUser")
    public BaseResponse<List<PracticeRecord>> listByUser(@RequestParam("userId") Long userId) {
        List<PracticeRecord> list = practiceRecordService.listRecordsByUserId(userId);
        return ResultUtils.success(list);
    }

    /**
     * 分页获取用户封装列表（仅管理员）
     *
     */
    @PostMapping("/list/page/vo")
    public BaseResponse<Page<PracticeRecord>> listRecordByPage(@RequestBody PracticeRecordQueryRequest practiceRecordQueryRequest) {
        ThrowUtils.throwIf(practiceRecordQueryRequest == null, ErrorCode.PARAMS_ERROR);
        long current = practiceRecordQueryRequest.getCurrent();
        long pageSize = practiceRecordQueryRequest.getPageSize();
        Page<PracticeRecord> practiceRecordPage = practiceRecordService.page(new Page<>(current, pageSize),
                practiceRecordService.getQueryWrapper(practiceRecordQueryRequest));
        Page<PracticeRecord> RecordPage = new Page<>(current, pageSize, practiceRecordPage.getTotal());
        List<PracticeRecord> RecordList = practiceRecordService.getRecordsList(practiceRecordPage.getRecords());
        RecordPage.setRecords(RecordList);
        return ResultUtils.success(RecordPage);
    }


    @PostMapping("/ask")
    public Mono<Map<String, String>> askAI(@RequestBody Map<String, String> body) {
        String question = body.get("question");
        // 调用你已有的 AI 智能体（假设 aiService.chat(prompt) 可用）
        return aiService.chat(question)
                .map(answer -> {
                    Map<String, String> result = Map.of("answer", answer);
                    System.out.println("AI问答接口返回内容：" + result);
                    return result;
                });
    }
}

