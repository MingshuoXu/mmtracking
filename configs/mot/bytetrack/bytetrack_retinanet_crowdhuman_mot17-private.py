# TODO: delete this file
_base_ = [
    '../../_base_/datasets/mot_challenge.py',
    '../../_base_/default_runtime.py',
]
# model settings
preprocess_cfg = dict(
    mean=[123.675, 116.28, 103.53],
    std=[58.395, 57.12, 57.375],
    to_rgb=True,
    pad_size_divisor=32)

model = dict(
    type='ByteTrack',
    preprocess_cfg=preprocess_cfg,
    detector=dict(
        type='mmdet.RetinaNet',
        backbone=dict(
            type='ResNet',
            depth=50,
            num_stages=4,
            out_indices=(0, 1, 2, 3),
            frozen_stages=1,
            norm_cfg=dict(type='BN', requires_grad=True),
            norm_eval=True,
            style='pytorch',
            init_cfg=dict(
                type='Pretrained', checkpoint='torchvision://resnet50')),
        neck=dict(
            type='FPN',
            in_channels=[256, 512, 1024, 2048],
            out_channels=256,
            start_level=1,
            add_extra_convs='on_input',
            num_outs=5),
        bbox_head=dict(
            type='RetinaHead',
            num_classes=80,
            in_channels=256,
            stacked_convs=4,
            feat_channels=256,
            anchor_generator=dict(
                type='AnchorGenerator',
                octave_base_scale=4,
                scales_per_octave=3,
                ratios=[0.5, 1.0, 2.0],
                strides=[8, 16, 32, 64, 128]),
            bbox_coder=dict(
                type='DeltaXYWHBBoxCoder',
                target_means=[.0, .0, .0, .0],
                target_stds=[1.0, 1.0, 1.0, 1.0]),
            loss_cls=dict(
                type='FocalLoss',
                use_sigmoid=True,
                gamma=2.0,
                alpha=0.25,
                loss_weight=1.0),
            loss_bbox=dict(type='L1Loss', loss_weight=1.0)),
        # model training and testing settings
        train_cfg=dict(
            assigner=dict(
                type='MaxIoUAssigner',
                pos_iou_thr=0.5,
                neg_iou_thr=0.4,
                min_pos_iou=0,
                ignore_iof_thr=-1),
            allowed_border=-1,
            pos_weight=-1,
            debug=False),
        test_cfg=dict(
            nms_pre=1000,
            min_bbox_size=0,
            score_thr=0.05,
            nms=dict(type='nms', iou_threshold=0.5),
            max_per_img=100)),
    motion=dict(type='KalmanFilter'),
    tracker=dict(
        type='ByteTracker',
        obj_score_thrs=dict(high=0.6, low=0.1),
        init_track_thr=0.7,
        weight_iou_with_det_scores=True,
        match_iou_thrs=dict(high=0.1, low=0.5, tentative=0.3),
        num_frames_retain=30))

# training schedule
train_cfg = dict(by_epoch=True, max_epochs=7)
val_cfg = dict(interval=7)
test_cfg = dict()

# learning rate
param_scheduler = [
    dict(
        type='LinearLR',
        start_factor=1.0 / 3,
        by_epoch=False,
        begin=0,
        end=500),
    dict(
        type='MultiStepLR',
        begin=0,
        end=7,
        by_epoch=True,
        milestones=[2, 5],
        gamma=0.1)
]

# optimizer
optimizer = dict(type='SGD', lr=0.01, momentum=0.9, weight_decay=0.0001)
default_hooks = dict(
    optimizer=dict(
        _delete_=True,
        type='OptimizerHook',
        grad_clip=dict(max_norm=35, norm_type=2)))