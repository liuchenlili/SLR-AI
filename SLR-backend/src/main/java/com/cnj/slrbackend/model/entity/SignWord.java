package com.cnj.slrbackend.model.entity;

import lombok.Data;

@Data
public class SignWord {
    private Long id;
    private String word;
    private String videoUrl;
    private String actionDesc;
    private String chineseMeaning;
}
