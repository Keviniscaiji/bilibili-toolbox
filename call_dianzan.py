import bili

bilibimain=bili.bilibili("CURRENT_FNVAL=80; _uuid=4FB40EA2-D1BC-42D3-9994-675015A4C56B34095infoc; blackside_state=1; rpdid=|(RYlRkYu)m0J'uY|Y)kmJJm; PVID=1; LIVE_BUVID=AUTO7516085820031103; SESSDATA=1e6d5734%2C1629319228%2C5eeea%2A21; bili_jct=9e94f48f76aec3630a5c490d4d22c6ee; DedeUserID=522965967; DedeUserID__ckMd5=9495dd843f32c3b7; sid=be3kep3a; buvid3=3818F0BE-F640-4561-ABCF-826CBB701F9B185013infoc; buvid_fp=3818F0BE-F640-4561-ABCF-826CBB701F9B185013infoc; buvid_fp_plain=3818F0BE-F640-4561-ABCF-826CBB701F9B185013infoc; CURRENT_QUALITY=80; fingerprint3=4c8b7b45c34aaf3dfe006379e478ccec; fingerprint=ae5e523f8c02a0329e5087675831b02b; fingerprint_s=ea52accb5ce8db9e6ff6b74a0795350c; bsource=share_source_qzone", "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36")

aid=bilibimain.BvtoAid("BV1qt4y127Ba")
print(aid)
bilibimain.dianzan(aid)