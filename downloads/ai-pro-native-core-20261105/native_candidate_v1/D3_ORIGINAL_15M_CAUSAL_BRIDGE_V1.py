"""TAC original D2→D3 15m-only causal bridge, TEST_ONLY, zero trading.

Append below all original scientific definitions in strategy.py. The
function uses ORIGINAL CanonicalBar, D2ReferenceSkeleton, EMA/ATR/Supertrend,
D3ReferenceSkeleton UPDATE-000/002/007/008 and frozen D3 parameters.
Independent price-path return, structural acceptance, 1h/4h and B5 role
evidence is NOT synthesized; do not interpret as complete D3 or entry-ready.
"""
def _tac_original_d3_15m_partial_from_exact_rows(symbol, raw_rows):
    if TAC_LIVE_ENABLED != 0:
        raise ValueError('TEST_ONLY_REQUIRED')
    if not raw_rows or len(raw_rows)>1024:
        raise ValueError('D3_PROSPECTIVE_HISTORY_UNAVAILABLE_OR_TRUNCATED')
    bars=[]
    for row in raw_rows:
        if type(row) is not dict or row.get('symbol')!=symbol or row.get('is_closed') is not True:
            raise ValueError('D3_EXACT_CLOSED_SOURCE_REQUIRED')
        bars.append(CanonicalBar.from_values(
            symbol=symbol,open_time=row['open_time'],close_time=row['close_time'],
            open=row['open'],high=row['high'],low=row['low'],close=row['close'],
            base_volume=row['base_volume'],quote_volume=row['quote_volume']))
    canon=canonicalize_15m(bars)
    if len(canon.records)!=len(bars) or canon.issues:
        raise ValueError('D3_ORIGINAL_D1_CANONICAL_INTEGRITY')
    official=current_partial_parameter_snapshot()
    if official.runtime_usable or official.complete_strategy_parameter_snapshot:
        raise ValueError('SCIENTIFIC_SNAPSHOT_FALSE_FREEZE')
    for name in ('theta_minor','theta_intermediate','theta_major'):
        slot=official.slot(name)
        if slot.state is not ParameterState.OPEN or slot.exact_value is not None:
            raise ValueError('UNAUTHORIZED_FROZEN_STRUCTURAL_VALUE')
    stop=official.slot('theta_stop')
    if stop.state is not ParameterState.LOCKED or stop.exact_value is not None:
        raise ValueError('OFFICIAL_THETA_STOP_STATE_MODIFIED')
    d2=D2ReferenceSkeleton(symbol=symbol,
        structural_params=_testonly_structural_exact(),
        frozen_params=frozen_d2_parameters(official))
    d3=D3ReferenceSkeleton.from_parameter_snapshot(official)
    e20,e50=EMARecurrence(20),EMARecurrence(50)
    atr=ATR14Recurrence()
    st=SupertrendRecurrence()
    candidates={}
    prior_episode=None
    prior_direction=TrendDirection.NONE
    prior_segment=None
    recorded={'candidate_snapshots':0,'prebar_geometry_updates':0,
        'original_update007_events':0,'original_update008_attempts':0,
        'original_update008_episodes':0,'D3_active_15m_source_cutoffs':0,
        'ema20_candidate_seen':0,'ema50_candidate_seen':0,
        'st_active_candidate_seen':0}
    cutoff=None
    for record in canon.records:
        bar=record.bar
        segment=record.canonical_segment_id
        if prior_segment is not None and segment!=prior_segment:
            # Explicitly block old boundary continuity after a source reset.
            prior_episode=None
            prior_direction=TrendDirection.NONE
            candidates={}
            d3=D3ReferenceSkeleton.from_parameter_snapshot(official)
        # UPDATE000 before any new data on the current observer bar.
        pre=d3.update_000_pre_bar_view(bar.open_time)
        for snapshot in pre.snapshots:
            if (snapshot.target_trend_episode_id!=prior_episode or
                snapshot.target_direction is not prior_direction):
                continue
            geo=d3.update_002_capture_geometry(
                bar=bar,information_cutoff=bar.close_time,snapshot=snapshot)
            recorded['prebar_geometry_updates']+=1
            # No made-up F3 return magnitude, no made-up D2 structural
            # acceptance or correct-side recovery. The original functions
            # must be allowed to remain unconfirmed when these are unknown.
            event=d3.update_007_interaction_break(
                snapshot=snapshot,geometry=geo,return_evidence=None,
                structural_acceptance=None,correct_side_recovery=None)
            recorded['original_update007_events']+=1
            if event.candidate_id not in candidates:
                raise ValueError('D3_CANDIDATE_LINEAGE_MISSING')
            recorded['original_update008_attempts']+=1
            episode=d3.update_008_anchor_lifecycle(
                candidate=candidates[event.candidate_id],
                target_trend_active=True,
                candidate_terminally_invalidated=(
                    event.terminal and event.break_state is BreakState.TRUE_BREAK),
                cutoff=bar.close_time)
            if episode is not None:
                recorded['original_update008_episodes']+=1
        ema20=e20.update(bar.close,segment_id=segment)
        ema50=e50.update(bar.close,segment_id=segment)
        a=atr.update(bar,segment_id=segment)
        st_point=st.update(bar,a,segment_id=segment)
        d2view=d2.advance_source_bar(bar,a,canonical_segment_id=segment)
        trend=d2view.update_006_trend
        prior_episode=trend.episode_id
        prior_direction=trend.direction
        prior_segment=segment
        cutoff=bar.close_time
        if (trend.episode_id is None or
            trend.direction not in (TrendDirection.LONG,TrendDirection.SHORT)):
            continue
        # Make ORIGINAL 15m boundary candidates after this source close.
        for family,line,st_direction in (
            (CandidateFamily.EMA20,ema20,None),
            (CandidateFamily.EMA50,ema50,None),
            (CandidateFamily.ST_ACTIVE,st_point.active_line,st_point.direction)):
            cand=build_candidate(symbol=symbol,source_timeframe_ms=900000,
                target_trend_episode_id=trend.episode_id,
                target_direction=trend.direction,family=family,
                line=line,source_scale=a,source_segment_id=segment,
                available_at=bar.close_time,source_continuity_ok=True,
                st_direction=st_direction,
                provenance={'source':'EXACT_ORIGINAL_15M_D1_MATH',
                    'scope':'TEST_ONLY_D3_15M_NOT_FULL_MULTI_TF'})
            snap=d3.update_008_register_candidate(cand)
            if snap is not None:
                candidates[cand.candidate_id]=cand
                recorded['candidate_snapshots']+=1
                recorded[family.value.lower()+'_candidate_seen']+=1
        recorded['D3_active_15m_source_cutoffs']+=1
    observed=recorded['prebar_geometry_updates']>0
    return {
        'schema':'TAC_ORIGINAL_D3_15M_PARTIAL_TEST_ONLY_V1',
        'status':('PARTIAL_ORIGINAL_D3_15M_CAUSAL_METHODS_EXECUTED'
                  if observed else 'BLOCKED_NO_ACTIVE_D3_15M_PREBAR_EVIDENCE'),
        'symbol':symbol,'cutoff':cutoff,'source_bars':len(canon.records),
        'last_original_d2_episode':prior_episode,
        'last_original_d2_direction':prior_direction.value,
        'trace':recorded,'original_update000_bar_calls':len(canon.records),
        'independent_D3_return_evidence':'NOT_AUTHENTICATED',
        'independent_D3_structural_acceptance':'NOT_AUTHENTICATED',
        'D3_1h_4h_and_B5_roles':'NOT_BOUND',
        'D4_F9_D5_UPDATE014_D6':'NOT_EXECUTED',
        'entry_ready':False,'TAC_LIVE_ENABLED':0,
        'orders':0,'fills':0,'trade_authorized':False
    }
