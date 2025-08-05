package com.cnj.slrbackend.service.service;


import com.baomidou.mybatisplus.extension.service.IService;
import com.cnj.slrbackend.model.entity.SignWord;

import java.util.List;

public interface SignWordService extends IService<SignWord> {
    List<SignWord> listAll();
    List<SignWord> search(String keyword);
    SignWord getById(Long id);
}
