#!/usr/bin/env python3
"""Patch residual Chinese UI strings that are outside the normal .po catalog."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path


HAN_RE = re.compile(r"[\u3400-\u9fff]")


TEXT_REPLACEMENTS: dict[str, str] = {
    # H5 smart text / voice-over UI strings.
    "直接Enter script，或用 AI 助手：找灵感、快速生文、提取文案": (
        "Enter a script directly, or use the AI assistant to find ideas, "
        "generate copy quickly, and extract copy"
    ),
    "正在Generate narration script": "Generating narration script",
    "需输入10字以上": "Enter at least 10 characters",
    '+"字"': '+" characters"',
    # H5 editor diagnostics that can leak to consoles/toasts in edge cases.
    "[contentState][apply] 数据异常: ": "[contentState][apply] Data error: ",
    "zoneState.allText是过时API，请换成zoneState.getModelText": (
        "zoneState.allText is deprecated. Use zoneState.getModelText instead"
    ),
    "外部没有传入 react-dom/server's renderToStaticMarkup 方法，无法渲染 react component": (
        "react-dom/server renderToStaticMarkup was not provided, so the React component cannot be rendered"
    ),
    # Non-UI comments in scripts/shaders. These are included so a deep text scan is quieter.
    "-- 没有扩展/腐蚀": "-- no dilation/erosion",
    "--测试用": "-- test only",
    "--实际用": "-- production",
    "//基准图": "// base image",
    "//原图": "// source image",
    "//滑竿": "// slider",
    "TODO：移到业务层": "TODO: move to the business layer",
    "用于min、max两张LUT图合并的情况，minLUT在上方，maxLUT在下方": (
        "Used when merging min and max LUT images; minLUT is above and maxLUT is below"
    ),
    "因为对两张LUT图做了合并，上半部分对应于intensity < 0.0的情况，下半部分对应于intensity > 0.0的情况": (
        "The two LUT images are merged; the upper half maps intensity < 0.0 and the lower half maps intensity > 0.0"
    ),
    "注意：此函数的参数以p来命名，但在该应用中（调色曲线），p主要指x坐标，要求x(t)与t的关系必须是单调的，才能用二分法找到t。": (
        "Note: this function names its parameter p, but in this app (color curves), p mainly refers to the x coordinate. "
        "x(t) must be monotonic so t can be found with binary search."
    ),
    "这里所讲的'单调'关系在调色曲线中一般是满足的，等同于y必须是x的函数，同一个x不允许有多个y与之对应。": (
        "The monotonic relationship described here is usually satisfied for color curves. It means y must be a function "
        "of x, so the same x cannot map to multiple y values."
    ),
    "色相调节本质上是把颜色从RGB空间转换到YUV空间，然后旋转UV来实现，": (
        "Hue adjustment converts color from RGB to YUV, then rotates UV,"
    ),
    "由于RGB转YUV，UV旋转，以及YUV转RGB都可以通过3x3矩阵来实现，所以最终可以合并成一个矩阵。": (
        "Because RGB-to-YUV, UV rotation, and YUV-to-RGB can all be implemented with 3x3 matrices, they can be merged into one matrix."
    ),
    "对比发现，当rgb三个数值的中位数与cmin，cmax距离都较远时，需要做一定的尺度修正; 另外修正因子跟曲线斜率也有一定关系，曲线越平就越不用修正。": (
        "Comparison shows that when the median RGB value is far from both cmin and cmax, some scale correction is needed; "
        "the correction factor also relates to curve slope, and flatter curves need less correction."
    ),
    "调节理论：": "Adjustment theory:",
    "色相：色相是颜色的基本属性，表示颜色在光谱中的位置（如红、黄、绿等），在HSL颜色空间中，色相由0到360度的角度表示。": (
        "Hue: hue is a basic color attribute that represents a color's position in the spectrum. In HSL, hue is represented as an angle from 0 to 360 degrees."
    ),
    "此处图片本身色相数值的计算采用了HSL的公式，但是色相调节使用的是矩阵法，即在YUV空间中旋转UV来实现。": (
        "Here the image hue value is calculated with the HSL formula, while hue adjustment uses a matrix method by rotating UV in YUV space."
    ),
    "饱和度：饱和度是颜色的纯度或鲜艳程度，此处饱和度的衡量使用rgb的最大值与最小值的差值。": (
        "Saturation: saturation is the purity or vividness of a color. Here it is measured by the difference between the maximum and minimum RGB values."
    ),
    "饱和度参数的默认值是1，表示不做饱和度调节，当参数为p时，会把原饱和度s调节为p*s，所以不同饱和度曲线之间耦合采用乘法。": (
        "The default saturation parameter is 1, meaning no saturation adjustment. When the parameter is p, the original saturation s becomes p*s, "
        "so different saturation curves are coupled by multiplication."
    ),
    "柱体": "cylinder",
    "锥体": "cone",
    "inputIntensity是在[0,1]范围内，用幂函数变换一下": (
        "inputIntensity is in the [0,1] range; transform it with a power function"
    ),
    "获取 self.entity 上的输入视频组件 (如果有缓存)": "Get the input video component on self.entity (if cached)",
    "使用 DilateErode 管线输出的 #MattingMask": "Use #MattingMask output from the DilateErode pipeline",
    "清理旧的视频组件（如果有）": "Clean up the old video component (if any)",
    "静态图片纹理": "static image texture",
    "获取 videoMaskSeq entity 上的 mask 视频组件": "Get the mask video component on the videoMaskSeq entity",
    "使用 maskRT 作为 mask 输入（Camera_videoMaskSeq 已将 mask 渲染到 maskRT）": (
        "Use maskRT as the mask input (Camera_videoMaskSeq has rendered the mask into maskRT)"
    ),
    "Camera_videoMaskSeq (order=2) 先将 mask 视频渲染到 maskRT，供后续管线读取": (
        "Camera_videoMaskSeq (order=2) first renders the mask video to maskRT for later pipeline reads"
    ),
    "单位：秒": "unit: seconds",
    "仅在路径真正变化时，清理旧资源并重新加载": "Only clean up old resources and reload when the path really changes",
    "清理旧的静态纹理": "Clean up the old static texture",
    "curTime 由外部 current_time 事件设置（单位：秒）": (
        "curTime is set externally by the current_time event (unit: seconds)"
    ),
    "relativeMediaStartTime 由外部传入": "relativeMediaStartTime is passed in externally",
    # Source-map comments from the H5 guide bundle.
    "该方法只有 SSR 场景下会执行": "This method only runs in SSR scenarios",
    "只需要拿到组件，不渲染，例如 SSR 和 微前端场景": (
        "Only get the component without rendering, such as in SSR and micro-frontend scenarios"
    ),
    "调用所有运行时插件，将入口文件 App 进行包裹": "Call all runtime plugins to wrap the entry App",
    "兼容 0.5.x 逻辑": "Compatible with 0.5.x logic",
    "类型处理，当 useErrMsg 为 true 则必填": "Type handling: required when useErrMsg is true",
    "直接使用 err_msg": "Use err_msg directly",
    "剪映处理": "Jianying handling",
    "使用 cefQuery": "Use cefQuery",
    "项目全局样式文件": "Project global style file",
    "该文件会被框架自动引入，无需手动引入": "This file is imported automatically by the framework; manual import is not required",
    "查看文档：": "Docs:",
}


BINARY_REPLACEMENTS: dict[str, dict[str, str]] = {
    "Contents/Frameworks/liblyra_cli_client.dylib": {
        "英雄时刻": "Hero Moment",
        "蒙太奇": "Montage",
        "子弹时间": "Bullet Time",
        "跳接": "J-Cut",
        "闪进": "F-In",
        "闪出": "F-Out",
        "自定义": "Custom",
    },
    "Contents/Frameworks/VideoFusionData.framework/VideoFusionData": {
        "定格": "Freeze",
    },
}


PACKED_TEXT_REPLACEMENTS: dict[str, str] = {
    # Lynx templates are length-prefixed binary bundles. Replacements are padded with spaces
    # to the exact original byte length, so the compiled template structure stays stable.
    "立即订阅": "Subscribe",
    "空间暂未订阅，订阅后可享无限额度": "No space plan; subscribe for unlimited quota",
    "无法添加更多品牌素材": "No more brand assets",
    "个人会员": "Individual",
    "小组会员": "Team",
    "小组云盘": "Team Cloud",
    "个人云盘": "My Cloud",
    "您本次自动订阅取消失败，请打开抖音App，点击我 - 右上角“我的钱包” - 抖音支付 - 设置 - 自动扣款管理 - 选择【剪映付费会员服务】进行解约操作": (
        "Auto-renew cancellation failed. Open Douyin: Me > My Wallet > Douyin Pay > Settings > Auto debit management > Jianying paid membership service to cancel."
    ),
    "您本次自动订阅取消失败，请打开微信App，点击我 - 钱包- 支付设置 - 自动续费 - 选择【剪映付费会员服务】进行解约操作": (
        "Auto-renew cancellation failed. Open WeChat: Me > Wallet > Payment settings > Auto-renewal > Jianying paid membership service to cancel."
    ),
    "您本次自动订阅取消失败，请打开支付宝App ，点击我的 - 设置 - 支付设置 - 免密支付/自动扣款 - 选择【剪映付费会员服务】进行解约操作": (
        "Auto-renew cancellation failed. Open Alipay: Me > Settings > Payment settings > Password-free payments/auto debit > Jianying paid membership service to cancel."
    ),
    "由于业务调整，小组云盘包将进行下线调整，无法继续提供购买服务，下线前购买的小组云盘包不受影响，可继续享受现有空间容量至云盘包到期，后续如需续享小组云空间容量可购买团队版": (
        "Due to business changes, the team cloud package will be discontinued and can no longer be purchased. Existing packages keep their storage until expiry; buy Team Edition to continue team cloud storage later."
    ),
    "小组云盘下线通知": "Cloud offline notice",
    "你收藏过": "Favorited",
    "最近买过": "Bought",
    "进阶": "Adv.",
    "基础": "Basic",
    "全阶段": "All",
    "团队版": "Team",
    "确定": "OK",
    "权益": "Perks",
    "基于平台治理和您的小组协作账号安全，平台会对一段时间内可加入的成员数量进行限制，如您遇到相关问题，可联系平台进行咨询。": (
        "For platform governance and team account security, member joins may be limited for a period. Contact support if this affects you."
    ),
    "确认购买后，您的Apple账户将被收取费用，订阅将会自动续订，除非在当前订阅结束前至少提前24小时关闭自动续订。您的账户将在当前订阅结束前的最后24小时里被收取续订费用，并确定续订开支。订阅后，您可以随时在AppleID的账户设置中管理续订和关闭自动续订。": (
        "After purchase, your Apple account will be charged. The subscription renews automatically unless auto-renew is turned off at least 24 hours before the current period ends. Renewal is charged within the final 24 hours. Manage or cancel renewal anytime in Apple ID settings."
    ),
    "素材越多，AI更容易选出好分镜": "More assets help AI pick better shots",
    "分析画面…": "Analyzing...",
    "努力合成中，请耐心等候": "Compositing, please wait",
    "即将跳转...": "Redirecting...",
    "为视频包装字幕、音乐和效果": "Add captions, music, and effects",
    "智能包装…": "Smart pack...",
    "合成视频…": "Compositing...",
    "AI给每句文案匹配合适的分镜": "AI matches shots to each line",
    "文案画面匹配…": "Text-shot match...",
    "AI写文案": "AI copy",
    "手动输入": "Manual",
    "投稿活动（": "Submit (",
    "《“剪映”AI功能付费服务协议》": '"Jianying" AI Paid Service Agreement',
    "网络异常，点击重试": "Network error, retry",
    "一个兑换码仅能兑换一次，请谨慎兑换；": "Each code can be redeemed once only; use carefully;",
    "兑换码存在有效期，过期无法兑换，请尽快使用；一般有效期为一年，具体以兑换码发放方的信息为准；": (
        "Codes expire and cannot be used after expiry. Use them soon. Usually valid for one year; see issuer details;"
    ),
    "兑换码需登录后才可兑换，请先登录再兑换；": "Log in before redeeming the code;",
    "会员&积分&云盘包权益有效时间与兑换时长一致；兑换会员赠送的积分值以兑换天数进行折算；": (
        "Membership, points, and cloud benefits match the redeemed duration; bonus points are prorated by redeemed days;"
    ),
    "本内容为虚拟产品，兑换后不可退款；": "Virtual product; no refund after redemption;",
    "兑换过程中如遇到问题，请到「剪映专业版-首页-右上角消息-意见反馈/在线支持」中进行反馈，客服团队将会处理；": (
        "For redemption issues, use Jianying Pro > Home > top-right messages > Feedback/Online Support; support will handle it;"
    ),
    "兑换权益流程最终解释，归剪映所有。": "Jianying has final interpretation rights.",
    "《剪映团队版服务协议(含自动续费条款)》": "Jianying Team Agreement (auto-renewal)",
    "《剪映会员服务协议(含自动续费条款)》": "Jianying Member Agreement (auto-renewal)",
    "《\"剪映\"会员服务协议（含自动续费条款）》": '"Jianying" Member Agreement (auto-renewal)',
    "《\"即梦\"会员服务协议（含自动续费条款）》": '"Dreamina" Member Agreement (auto-renewal)',
    "联合会员权益直接下发至本设备关联的即梦APP账号中，用户可使用剪映账号登录享受权益；": (
        "Benefits go to the linked Dreamina account; log in with Jianying to use them;"
    ),
    "发放后不可通过换绑账号等方式进行转让/转移；": "Cannot transfer after issue, including by rebinding accounts;",
    "联合会员权益从购买当日生效，订单到期自动续费，可随时取消": (
        "Starts on purchase day, auto-renews at expiry, cancel anytime"
    ),
    "即梦VIP下发成功": "Dreamina VIP issued",
    "联合会员为剪映联合合作方（醒图或即梦）推出的新型会员权益产品。用户购买联合会员并相应激活会员权益后，用户可在剪映及合作方享受对应的会员产品权益，权益详见各产品会员权益介绍。": (
        "Joint membership is a new benefits product from Jianying and partners (Xingtu or Dreamina). After purchase and activation, benefits are available in Jianying and the partner app; see each product's benefits."
    ),
    "什么是联合会员？": "Joint membership?",
    "开通后，开通过剪映（VIP/SVIP/团队版）及合作方会员的用户在双方原会员时长基础上叠加。未开通过剪映会员服务（VIP/SVIP/团队版）及合作方会员的新用户，开通联合会员后服务时长则自开通日起算。如遇到网络延迟，请用户在24小时内查看会员到账情况。": (
        "After activation, existing Jianying (VIP/SVIP/Team) and partner membership time is extended on top of current time. New users start from activation. If delayed, check within 24 hours."
    ),
    "开通后会员时长如何计算？": "How is duration counted?",
    "剪映会员如何领取?": "How to claim Jianying?",
    "剪映会员权益将自动发放至剪映账号，若剪映账号已有会员权益，会员时长将在已有会员权益时长基础上相应叠加本次会员权益时长。": (
        "Jianying benefits are issued to your Jianying account. Existing membership time is extended by this benefit duration."
    ),
    "即梦会员如何领取?": "How to claim Dreamina?",
    "即梦会员权益将自动发放至剪映账号关联的即梦账号中，用户开通剪映X即梦联合会员后，可在即梦APP内使用剪映账号登录享受联合会员权益。若即梦账号已有会员权益，会员时长将在已有会员权益时长基础上相应叠加本次会员权益时长。": (
        "Dreamina benefits go to the Dreamina account linked with Jianying. After buying Jianying x Dreamina, log in to Dreamina with Jianying. Existing Dreamina time is extended."
    ),
    "联合会员如何领取？": "How to claim?",
    "在使用过程中遇到的任何问题，可以点击剪映App内【我的】-【帮助中心】-【在线咨询】；醒图App内【我的】-【？（左上角）】-【意见反馈】咨询客服；即梦APP内【我】-【设置（左上角）】-【帮助中心】-【意见反馈】咨询客服": (
        "For issues, contact support in Jianying App > Me > Help Center > Online consultation; Xingtu App > Me > ? > Feedback; Dreamina App > Me > Settings > Help Center > Feedback"
    ),
    "如何与客服取得联系？": "Contact support?",
    "暂无更多数据": "No more data",
    "加载失败，请点击重试": "Load failed, retry",
    "暂无数据": "No data",
    "企业/事业单位": "Company/Institution",
    "企业单位": "Company",
    "非企业单位": "Non-company",
    "个人": "Person",
    "电子发票（增值税专用发票）": "VAT special e-invoice",
    "电子发票（普通发票）": "Standard e-invoice",
    "剪映网页版": "JY Web",
    "剪映专业版": "JY Pro",
    "剪映移动版": "JY Mobile",
    "您的账号操作退款次数已达上限，为保证账号安全，暂不支持自主申请退款，如有问题，请联系客服": (
        "Refund request limit reached. For account security, self-service refund is unavailable. Contact support for help"
    ),
    "申请次数已达上限": "Request limit reached",
    "会员用户可申请退款，审核通过后可退订单剩余时长金额（按退款申请日期到会员订单结束日期的时长占订单总时长的比例，进行退款）": (
        "Members may request a refund. If approved, the remaining order time is refunded based on the share from request date to order end date."
    ),
    "非剪映官方客户端内购买，或账号存在异常/风险状态，无法退款": (
        "Purchases outside official Jianying clients or risky accounts cannot be refunded"
    ),
    "同一用户每年最多退款3次": "Up to 3 refunds per user per year",
    "苹果订单或其他特殊情况退款，可联系人工客服": "For Apple orders or special cases, contact support",
    "退款规则": "Refund rules",
    "智能识别视频内容并一键添加素材": "AI detects video and adds assets",
    "该功能需要上传草稿至云端识别视频内容并一键包装，不会存储或泄露您的信息": (
        "Uploads draft to cloud to detect video and package it; your info is not stored or leaked"
    ),
    "智能包装": "Smart pack",
    "智能文案": "AI copy",
    "可智能修饰、加工文案内容": "AI polishes and edits copy",
    "可智能精简、提炼文案内容": "AI summarizes copy",
    "可智能扩写、丰富文案内容": "AI expands copy",
    "加载失败，点击重试": "Load failed, retry",
    "cccreator.dll 加载失败": "cccreator.dll load failed",
    "加载失败。%1": "Load failed. %1",
    "加载失败，": "Load failed,",
    "加载失败": "Load failed",
    "加载中，请稍等一下": "Loading, please wait",
    "加载中": "Loading",
    "Net error   ，请刷新重试": "Net error, refresh and retry",
    "Net error   ，发光效果加载失败": "Net error, glow failed",
    "运行在低于win7的系统兼容模式下": "Running in compatibility mode below Win7",
    "网络异常，该草稿中所含有的字幕结果无法读取，可检查网络后重试": (
        "Net error. Caption data in this draft cannot be read; check network and retry"
    ),
    "网络异常": "Net error",
    "导入字体失败": "Font import failed",
    "打开草稿失败": "Draft open failed",
    "恢复购买失败": "Restore failed",
    "保存失败，请检查网络": "Save failed; check network",
    "保存失败": "Save failed",
    "获取路径失败，点击重试": "Get path failed, retry",
    "素材加载失败": "Media load failed",
    "面板加载失败": "Panel load failed",
    "加载失败展示": "load fail view",
    "支付方式": "Payment",
    "管理空间": "Manage space",
    "是否继续进入编辑？": "Continue to editor?",
    "文本朗读中...": "Reading text...",
    "文本识别中...": "Text OCR...",
    "识别视频中歌曲并自动生成字幕": "Detect songs and make captions",
    "素材美观度低": "Low visual quality",
    "素材下载失败，": "Download failed,",
    "本地字体": "Local font",
    "粉丝自制": "Fan-made",
    "粉丝": "Fans",
    "远-近": "Far-Nr",
    "快传成功": "Quick sent",
    "快传至%1": "Fast to %1",
    "快传中断": "Fast stopped",
    "英雄时刻": "Hero Moment",
    "蒙太奇": "Montage",
    "子弹时间": "Bullet Time",
    "跳接": "J-Cut",
    "闪进": "F-In",
    "闪出": "F-Out",
    "自定义": "Custom",
    "定格": "Freeze",
}


PACKED_BINARY_PAYLOADS = [
    "Contents/Frameworks/libVECreator.dylib",
    "Contents/Frameworks/libAICreator.dylib",
    "Contents/Frameworks/libvideoeditor.dylib",
    "Contents/Frameworks/VECrashHandler.app/Contents/MacOS/VECrashHandler",
    "Contents/Frameworks/VEHelper.app/Contents/MacOS/VEHelper",
    "Contents/Frameworks/Chromium Embedded Framework.framework/Versions/A/Resources/zh_CN.lproj/locale.pak",
    "Contents/Frameworks/Chromium Embedded Framework.framework/Versions/A/Resources/zh_TW.lproj/locale.pak",
]


TEXT_SUFFIXES = {
    ".css",
    ".frag",
    ".glsl",
    ".html",
    ".js",
    ".json",
    ".lua",
    ".map",
    ".metal",
    ".plist",
    ".strings",
    ".txt",
    ".xml",
}


def patch_text_files(app: Path) -> tuple[int, int]:
    files_changed = 0
    replacements = 0
    for path in app.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            original = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        updated = original
        for old, new in TEXT_REPLACEMENTS.items():
            count = updated.count(old)
            if count:
                updated = updated.replace(old, new)
                replacements += count
        if updated != original:
            path.write_text(updated, encoding="utf-8")
            files_changed += 1
    return files_changed, replacements


def patch_binary_files(app: Path) -> tuple[int, int]:
    files_changed = 0
    replacements = 0
    for rel, mapping in BINARY_REPLACEMENTS.items():
        path = app / rel
        data = path.read_bytes()
        updated = data
        for old, new in mapping.items():
            old_b = old.encode("utf-8")
            new_b = new.encode("utf-8")
            if len(new_b) > len(old_b):
                raise ValueError(f"{new!r} is longer than {old!r} in bytes")
            count = updated.count(old_b)
            if count:
                updated = updated.replace(old_b, new_b + (b"\0" * (len(old_b) - len(new_b))))
                replacements += count
        if updated != data:
            path.write_bytes(updated)
            files_changed += 1
    return files_changed, replacements


def patch_packed_template_files(app: Path) -> tuple[int, int]:
    root = app / "Contents/Resources/lynx_config"
    if not root.exists():
        return 0, 0

    encoded = encode_packed_replacements()

    files_changed = 0
    replacements = 0
    for path in root.rglob("template.js"):
        data = path.read_bytes()
        updated = apply_packed_replacements(data, encoded)
        if updated != data:
            replacements += sum(data.count(old_b) for old_b, _ in encoded)
            path.write_bytes(updated)
            files_changed += 1
    return files_changed, replacements


def encode_packed_replacements() -> list[tuple[bytes, bytes]]:
    encoded: list[tuple[bytes, bytes]] = []
    for old, new in sorted(PACKED_TEXT_REPLACEMENTS.items(), key=lambda item: len(item[0].encode("utf-8")), reverse=True):
        old_b = old.encode("utf-8")
        new_b = new.encode("utf-8")
        if len(new_b) > len(old_b):
            raise ValueError(
                f"packed replacement too long: {old!r} ({len(old_b)} bytes) -> {new!r} ({len(new_b)} bytes)"
            )
        encoded.append((old_b, new_b + (b" " * (len(old_b) - len(new_b)))))
    return encoded


def apply_packed_replacements(data: bytes, encoded: list[tuple[bytes, bytes]]) -> bytes:
    updated = data
    for old_b, new_b in encoded:
        if old_b in updated:
            updated = updated.replace(old_b, new_b)
    return updated


def patch_packed_binary_payloads(app: Path) -> tuple[int, int]:
    encoded = sorted(encode_packed_replacement_cores(), key=lambda item: len(item[0]), reverse=True)
    po_segments = dict(encode_po_replacement_cores(app))
    files_changed = 0
    replacements = 0
    for rel in PACKED_BINARY_PAYLOADS:
        path = app / rel
        if not path.exists():
            continue
        data = path.read_bytes()
        updated, count = apply_contextual_binary_replacements(data, encoded)
        updated, po_count = apply_nul_segment_replacements(updated, po_segments)
        replacements += count + po_count
        if updated != data:
            path.write_bytes(updated)
            files_changed += 1
    return files_changed, replacements


def encode_packed_replacement_cores() -> list[tuple[bytes, bytes]]:
    encoded: list[tuple[bytes, bytes]] = []
    for old, new in PACKED_TEXT_REPLACEMENTS.items():
        old_b = old.encode("utf-8")
        new_b = new.encode("utf-8")
        if len(new_b) <= len(old_b):
            encoded.append((old_b, new_b))
    return encoded


def apply_contextual_binary_replacements(data: bytes, encoded: list[tuple[bytes, bytes]]) -> tuple[bytes, int]:
    updated = data
    total = 0
    for old_b, new_core in encoded:
        if old_b not in updated:
            continue
        out = bytearray()
        pos = 0
        count = 0
        while True:
            idx = updated.find(old_b, pos)
            if idx < 0:
                out.extend(updated[pos:])
                break
            out.extend(updated[pos:idx])
            next_byte = updated[idx + len(old_b) : idx + len(old_b) + 1]
            pad = b"\0" if next_byte == b"\0" else b" "
            out.extend(new_core + (pad * (len(old_b) - len(new_core))))
            pos = idx + len(old_b)
            count += 1
        updated = bytes(out)
        total += count
    return updated, total


def apply_nul_segment_replacements(data: bytes, replacements: dict[bytes, bytes]) -> tuple[bytes, int]:
    if not replacements:
        return data, 0
    parts = data.split(b"\0")
    count = 0
    changed = False
    for i, part in enumerate(parts):
        new_core = replacements.get(part)
        if new_core is None:
            continue
        if len(new_core) > len(part):
            continue
        parts[i] = new_core + (b"\0" * (len(part) - len(new_core)))
        count += 1
        changed = True
    if not changed:
        return data, 0
    return b"\0".join(parts), count


def po_unescape(s: str) -> str:
    return ast.literal_eval(s)


def split_entries(text: str) -> list[str]:
    entries: list[str] = []
    cur: list[str] = []
    for line in text.splitlines():
        if not line.strip():
            if cur:
                entries.append("\n".join(cur))
                cur = []
            continue
        cur.append(line)
    if cur:
        entries.append("\n".join(cur))
    return entries


def field_value(entry: str, field: str) -> str | None:
    lines = entry.splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith(field + " "):
            out.append(po_unescape(line[len(field) + 1 :]))
            i += 1
            while i < len(lines) and lines[i].startswith('"'):
                out.append(po_unescape(lines[i]))
                i += 1
            return "".join(out)
        i += 1
    return None


def read_po(path: Path) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for entry in split_entries(path.read_text(encoding="utf-8")):
        msgid = field_value(entry, "msgid")
        msgstr = field_value(entry, "msgstr")
        if msgid is not None and msgstr is not None:
            mapping[msgid] = msgstr
    return mapping


def encode_po_replacement_cores(app: Path) -> list[tuple[bytes, bytes]]:
    original_po = Path("/Applications/VideoFusion-macOS.app/Contents/Resources/po/zh-Hans.po")
    translated_po = app / "Contents/Resources/po/zh-Hans.po"
    if not original_po.exists() or not translated_po.exists():
        return []

    original = read_po(original_po)
    translated = read_po(translated_po)
    encoded: dict[bytes, bytes] = {}
    for msgid, old in original.items():
        new = translated.get(msgid)
        if not old or not new:
            continue
        if not HAN_RE.search(old) or HAN_RE.search(new):
            continue
        old_b = old.encode("utf-8")
        new_b = new.encode("utf-8")
        if len(new_b) <= len(old_b):
            encoded[old_b] = new_b
    return sorted(encoded.items(), key=lambda item: len(item[0]), reverse=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("app", type=Path)
    args = parser.parse_args()

    app = args.app.resolve()
    text_files, text_replacements = patch_text_files(app)
    binary_files, binary_replacements = patch_binary_files(app)
    packed_files, packed_replacements = patch_packed_template_files(app)
    packed_binary_files, packed_binary_replacements = patch_packed_binary_payloads(app)
    print(f"text_files_changed={text_files} text_replacements={text_replacements}")
    print(f"binary_files_changed={binary_files} binary_replacements={binary_replacements}")
    print(f"packed_template_files_changed={packed_files} packed_template_replacements={packed_replacements}")
    print(f"packed_binary_files_changed={packed_binary_files} packed_binary_replacements={packed_binary_replacements}")


if __name__ == "__main__":
    main()
