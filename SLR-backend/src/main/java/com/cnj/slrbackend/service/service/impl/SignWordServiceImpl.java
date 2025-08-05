package com.cnj.slrbackend.service.service.impl;

import com.baomidou.mybatisplus.extension.service.impl.ServiceImpl;
import com.cnj.slrbackend.mapper.SignWordMapper;
import com.cnj.slrbackend.mapper.UserMapper;
import com.cnj.slrbackend.model.entity.SignWord;
import com.cnj.slrbackend.model.entity.User;
import com.cnj.slrbackend.service.service.SignWordService;
import com.cnj.slrbackend.service.service.UserService;
import jakarta.annotation.Resource;
import org.springframework.stereotype.Service;

 import java.util.List;

@Service
public class SignWordServiceImpl extends ServiceImpl<SignWordMapper, SignWord>
        implements SignWordService {
    @Resource
    private SignWordMapper signWordMapper;

    @Override
    public List<SignWord> listAll() {
        return signWordMapper.selectList(null);
    }

    @Override
    public List<SignWord> search(String keyword) {
        System.out.println("Searching for keyword: " + keyword);
        return signWordMapper.searchByKeyword(keyword);
    }

    @Override
    public SignWord getById(Long id) {
        return signWordMapper.selectById(id);
    }
}





