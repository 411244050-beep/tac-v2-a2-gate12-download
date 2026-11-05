# Binance AI Pro TAC 原版候选 — 实际 batch 消费补丁 V2

**针对当前已经通过平台静态校验的工作区文件**，不是替换原 TAC，也不是独立的新策略。当前平台报告的工作区指纹：

- \`strategy/strategy.py\`: SHA256 \`7b4c55e5a1ff1d5ea71fa31d471653e40627f4826f93951d18f908adb10f297c\`，258797 bytes
- \`strategy/spec.yaml\`: SHA256 \`72e271a69bc28f476e768256fa1e557f4864b47fa289237e0d8b1532d0cf2e1b\`，816 bytes

**先确认当前文件指纹**。如果平台工作区不是这个修订版，不要覆盖原文件，先以实际现存源码定位精确补丁位置。不要从本公共目录重新下载旧 \`strategy.py\` 覆盖已修改版本。

## 根因及最小改动

原版候选在每次 \`await native_exact_15m_fetch(symbol)\` 后直接把返回包当作单个 K 线事件调用 \`_native_exact_closed_kline(receipt,symbol)\`；真实平台 \`kline_stream\` 返回**整批 \`batch\` 未读事件**。必须逐条、只消费一次，对每个 symbol 保存累计 dropped 基线并按时间无缺口合并，同时禁止无验证的 \`[-1024:]\` 截断后假冒 D2 持续状态。

只变更**后部候选绑定层**，不要改动前 243903 字符的原版 D1–D6/F9，别改动平台已修复的 \`interval\`、Spec \`from/to\`、D3 绝对引用、映射类型兼容和结构腿异常诊断。把以下函数（纯辅助，不能单独发送交易指令）插入 \`@workflow\` 之前；如果原工作区已有同名函数，停止，不做双重 patch。

\`\`\`python
def _native_batch_to_closed_exact_rows(receipt, symbol, prior_drop):
    if receipt is None:
        return (),prior_drop  # first call: subscribe-only, NOT a closed bar
    if type(receipt) is not dict or type(receipt.get('batch')) is not list:
        raise ValueError('NATIVE_BATCH_LIST_REQUIRED')
    dropped=receipt.get('dropped')
    if type(dropped) is not int or dropped<0:
        raise ValueError('NATIVE_DROPPED_COUNTER_INVALID')
    if prior_drop is None and dropped!=0:
        raise ValueError('NATIVE_PREEXISTING_DROPPED')
    if prior_drop is not None and dropped!=prior_drop:
        raise ValueError('NATIVE_DROPPED_CHANGED')
    if receipt.get('reconnects',0)!=0:
        raise ValueError('NATIVE_RECONNECT_UNVERIFIED')
    closed=[]
    for event in receipt['batch']:
        row=_native_exact_closed_kline(event,symbol)
        if row is None:continue
        if closed and row['open_time']!=closed[-1]['open_time']+900000:
            raise ValueError('NATIVE_DUPLICATE_GAP_OUT_OF_ORDER_IN_BATCH')
        closed.append(row)
    return tuple(closed),dropped

def _native_append_exact_nontruncated_history(old,new):
    rows=list(old)
    for item in new:
        if rows and item['open_time']!=rows[-1]['open_time']+900000:
            raise ValueError('NATIVE_CROSS_READ_DUPLICATE_GAP_OUT_OF_ORDER')
        if len(rows)>=MAX_EXACT_SOURCE_BARS:
            raise ValueError('ORIGINAL_D2_TRUNCATION_EQUIVALENCE_UNPROVEN')
        rows.append(item)
    return rows

def _native_528_same_cutoff_status(rows):
    if type(rows) is not dict or set(rows)!=set(FROZEN_528_SYMBOLS):
        raise ValueError('FROZEN_528_IDENTITY_NOT_EXACT')
    if any(not rows[s] for s in FROZEN_528_SYMBOLS):
        return 'BLOCKED_PROSPECTIVE_SUBSCRIPTION_OR_WARMUP_EMPTY'
    latest={rows[s][-1]['close_time'] for s in FROZEN_528_SYMBOLS}
    if len(latest)!=1:
        return 'BLOCKED_528_CURRENT_CUTOFF_MISMATCH'
    from datetime import datetime,timezone
    now=int(datetime.now(timezone.utc).timestamp()*1000)
    expected=(now//900000)*900000-1
    return ('PASS_EXACT_528_CURRENT_CUTOFF_SOURCE_ONLY'
            if next(iter(latest))==expected
            else 'BLOCKED_528_STALE_OR_ROLLOVER')
\`\`\`

### 将当前 \`@workflow original_tac_testonly_workflow\` 的有权限分支改为

保留目前的 \`TAC_LIVE_ENABLED=0\` 和 \`NATIVE_528_PROSPECTIVE_STREAM_AUTHORIZED=False\` 默认检查，不得自动打开。

\`\`\`python
    previous=ctx.state.get('tac_original_exact_closed_15m_v1',{})
    previous_drops=ctx.state.get('tac_original_dropped_15m_v1',{})
    if type(previous) is not dict or type(previous_drops) is not dict:
        raise ValueError('CTX_STATE_NOT_DICTIONARY')
    collected={}
    next_drops={}
    for symbol in FROZEN_528_SYMBOLS:
        receipt=await native_exact_15m_fetch(symbol)
        new_bars,new_dropped=_native_batch_to_closed_exact_rows(
            receipt,symbol,previous_drops.get(symbol))
        collected[symbol]=_native_append_exact_nontruncated_history(
            previous.get(symbol,()),new_bars)
        next_drops[symbol]=new_dropped
    status=_native_528_same_cutoff_status(collected)
    ctx.state['tac_original_exact_closed_15m_v1']=collected
    ctx.state['tac_original_dropped_15m_v1']=next_drops
    if status!='PASS_EXACT_528_CURRENT_CUTOFF_SOURCE_ONLY':
        return {'status':status,'target':528,'d1d2_computed':0,
                'D3_D4_F9_D5_UPDATE014_D6':'NOT_BOUND',
                'TAC_LIVE_ENABLED':0,'entry_ready':False,'orders':0}
    return await native_original_core_compute(collected)
\`\`\`

If exact current names differ, use the actual workspace names and **do not** change original semantics. This code assumes documented response \`{"batch": [...], "dropped": int}\`. If current platform returns a different nested shape, inspect a safe documented example and adapt precisely, then run negative tests; no guessing or silent fallback.

## Verified scope and limitations

- Local patcher (AST-preserving for all non-workflow original top-level functions) tested on the preserved source candidate, with **10/10 offline batch tests passed**. This is **not** an AI Pro native validation of the modified working file; the actual restored platform SHA must be verified.
- Invalid/missing \`batch\`, \`dropped\`, float OHLC, duplicate, missed close, reconnect and rollover fail closed. Current 528 exchange status (e.g. nontrading/settling) must be integrated from native verified metadata later: **do not silently downscope 528**.
- This stage **only fixes D1/D2 prospective source ingestion**. D3/D4/F9/formal D5/UPDATE014/D6 **remain disconnected** and cannot be claimed complete. Native checkpoint durability and long-term incremental semantic equivalence remain unverified; max 1024 history is a deliberate **BLOCK** rather than hidden reset.
- Run native \`validate_code\` and \`validate_spec\` on the corrected actual workspace, plus negative unit tests if available. Do not \`audit_code\` or deploy a production strategy before end-to-end core binding exists.
- \`TAC_LIVE_ENABLED=0\`, no account access, orders, Paper/Live, manually fabricated evidence, trade or execution authority.

## Next implementation after batch fix

Original D3 calls must bind actual D2 emitted pivots/episode + original EMA20/EMA50/ST (source timeframe and next-bar views), then original UPDATE000/002/007/008 and B5. D4 must use the original \`update_011\` four true source evidence families. Formal D5 must use the Oct 6 ten-slot policy, not superseded original PORT007; UPDATE014 requires actual cutoff-stage ledger, and D6 protection remains nontrading until platform resume and hard-stop evidence. Build and compare stages in order; never call the mere existence of original source functions a working pipeline.
