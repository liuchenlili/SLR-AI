package com.cnj.slrbackend.controller;


import com.cnj.slrbackend.model.entity.SignWord;
import com.cnj.slrbackend.service.service.SignWordService;
import jakarta.annotation.Resource;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/signWord")
public class SignWordController {
    @Resource
    private SignWordService signWordService;

    /**
     * 获取所有词汇
     */
    @GetMapping("/list")
    public List<SignWord> listAll() {
        return signWordService.listAll();
    }

    /**
     * 按关键字模糊查询
     */
    @GetMapping("/search")
    public List<SignWord> search(@RequestParam String keyword) {
        return signWordService.search(keyword);
    }

    /**
     * 查询单个
     */
    @GetMapping("/{id}")
    public SignWord getById(@PathVariable Long id) {
        return signWordService.getById(id);
    }
}

