"""Additional TEST_ONLY original TAC D2→D3 15m/1h/4h causal stage binding.

This adapter is intended to be appended AFTER original 91-module definitions in
Binance AI Pro's already-validated workspace source. It does not override any
frozen original scientific function or mutate the OPEN/LOCKED snapshot.

No D3 independent return or structural acceptance evidence is forged; no B5
contact zone/qualified use, D4 market event, entry-ready or trading intent is
created. Incremental state, HTF epoch continuity and real native stream are
NOT yet proved; use only for bounded exact source replay engineering tests.
"""

def _tac_original_multitf_d3_testonly(symbol, raw_rows):
    if TAC_LIVE_ENABLED != 0:
        raise ValueError('TAC_TEST_ONLY_NONTRADING_REQUIRED')
    if type(symbol) is not str or not symbol or not raw_rows or len(raw_rows)>1024:
        raise ValueError('TAC_EXACT_HISTORY_REQUIRED_UNTRUNCATED')
    bars=[]
    for r in raw_rows:
        if type(r) is not dict or r.get('symbol')!=symbol or r.get('is_closed') is not True:
            raise ValueError('TAC_EXACT_CLOSED_BAR_REQUIRED')
        bars.append(CanonicalBar.from_values(symbol=symbol,
            open_time=r['open_time'],close_time=r['close_time'],
            open=r['open'],high=r['high'],low=r['low'],close=r['close'],
            base_volume=r['base_volume'],quote_volume=r['quote_volume']))
    d1=canonicalize_15m(bars)
    if d1.issues or len(d1.records)!=len(bars):
        raise ValueError('TAC_D1_SOURCE_CONTINUITY_BLOCKED')
    snapshot=current_partial_parameter_snapshot()
    if snapshot.complete_strategy_parameter_snapshot or snapshot.runtime_usable:
        raise ValueError('TAC_FALSE_SCIENCE_SNAPSHOT')
    theta=[]
    for name,raw in (
        ('theta_minor','0.655417496698647720797643159793938746032740795679425'),
        ('theta_intermediate','1.7477799911963939221270484261171699894206421218118'),
        ('theta_major','3.4955599823927878442540968522343399788412842436236')):
        sl=snapshot.slot(name)
        if sl.state is not ParameterState.OPEN or sl.exact_value is not None:
            raise ValueError('TAC_TEST_ONLY_SCIENTIFIC_STATUS_DRIFT:'+name)
        theta.append(Fraction(Decimal(raw)))
    stop=snapshot.slot('theta_stop')
    if stop.state is not ParameterState.LOCKED or stop.exact_value is not None:
        raise ValueError('TAC_D5_STOP_GOVERNANCE_DRIFT')
    d2=D2ReferenceSkeleton(symbol=symbol,
        structural_params=StructuralScaleParameters(*theta),
        frozen_params=frozen_d2_parameters(snapshot))
    d3=D3ReferenceSkeleton.from_parameter_snapshot(snapshot)
    intervals=(900000,3600000,14400000)
    tools={ms:{'ema20':EMARecurrence(20),'ema50':EMARecurrence(50),
               'atr':ATR14Recurrence(),'st':SupertrendRecurrence()}
           for ms in intervals}
    latest_by_tf={}
    trend_episode_before=None
    trend_direction_before=TrendDirection.NONE
    candidates={}
    counter={
      '15m_completed_bars':0,'1h_completed_bars':0,'4h_completed_bars':0,
      'candidate_snapshots_15m':0,'candidate_snapshots_1h':0,'candidate_snapshots_4h':0,
      'candidate_registered_15m':0,'candidate_registered_1h':0,'candidate_registered_4h':0,
      'prebar_snapshots':0,'geometry_calls':0,'update007_calls':0,
      'geometry_15m':0,'geometry_1h':0,'geometry_4h':0,
      'update008_calls':0,'anchor_episodes':0,'b5_confirmed_zone_count':0,
      'd4_authenticated_market_events':0,'actual_15m_trend_episodes':0}
    last_d2=None
    diagnostic_d4_calls=0
    def _feed_one_source_bar(source_bar,ms,segment):
        t=tools[ms]
        v20=t['ema20'].update(source_bar.close,segment_id=segment)
        v50=t['ema50'].update(source_bar.close,segment_id=segment)
        atr=t['atr'].update(source_bar,segment_id=segment)
        st=t['st'].update(source_bar,atr,segment_id=segment)
        d2view=d2.advance_source_bar(source_bar,atr,
                                      canonical_segment_id=segment)
        latest_by_tf[ms]=(v20,v50,atr,st,d2view)
        counter[{900000:'15m',3600000:'1h',14400000:'4h'}[ms]+'_completed_bars']+=1
        return d2view
    def _register_candidates(source_bar,ms,target_trend):
        if (target_trend.episode_id is None or target_trend.direction not in
            (TrendDirection.LONG,TrendDirection.SHORT)):
            return
        e20,e50,atr,st,_=latest_by_tf[ms]
        for family,line,st_direction in (
          (CandidateFamily.EMA20,e20,None),
          (CandidateFamily.EMA50,e50,None),
          (CandidateFamily.ST_ACTIVE,st.active_line,st.direction)):
            candidate=build_candidate(symbol=symbol,source_timeframe_ms=ms,
               target_trend_episode_id=target_trend.episode_id,
               target_direction=target_trend.direction,family=family,
               line=line,source_scale=atr,source_segment_id=segment,
               available_at=source_bar.close_time,source_continuity_ok=True,
               st_direction=st_direction,
               provenance={'source':'ORIGINAL_D1_COMPLETED_SOURCE_TF',
                           'mode':'TEST_ONLY_NONTRADING_NOT_ENTRY_EVIDENCE'})
            boundary=d3.update_008_register_candidate(candidate)
            counter['candidate_registered_'+{900000:'15m',3600000:'1h',14400000:'4h'}[ms]]+=1
            if boundary is not None:
                candidates[candidate.candidate_id]=candidate
                counter['candidate_snapshots_'+{900000:'15m',3600000:'1h',14400000:'4h'}[ms]]+=1
    for i,rec in enumerate(d1.records):
        bar=rec.bar
        segment=rec.canonical_segment_id
        same_bar_d3_events=[]
        # Exact original UPDATE000: sample only snapshots available BEFORE
        # the observer bar opens. New HTF/15m candidates arise AFTER its close.
        previous=d3.update_000_pre_bar_view(bar.open_time)
        for old in previous.snapshots:
            if (old.target_trend_episode_id!=trend_episode_before or
                old.target_direction is not trend_direction_before):
                continue
            counter['prebar_snapshots']+=1
            geom=d3.update_002_capture_geometry(
                bar=bar,information_cutoff=bar.close_time,snapshot=old)
            counter['geometry_calls']+=1
            by_tf={900000:'15m',3600000:'1h',14400000:'4h'}.get(old.source_timeframe_ms)
            if by_tf is None:
                raise ValueError('UNEXPECTED_ORIGINAL_D3_SOURCE_TF')
            counter['geometry_'+by_tf]+=1
            event=d3.update_007_interaction_break(snapshot=old,geometry=geom,
                 return_evidence=None,structural_acceptance=None,
                 correct_side_recovery=None)
            counter['update007_calls']+=1
            same_bar_d3_events.append(event)
            if event.candidate_id not in candidates:
                raise ValueError('D3_EVENT_MISSING_ORIGINAL_CANDIDATE_ID')
            episode=d3.update_008_anchor_lifecycle(
                candidate=candidates[event.candidate_id],
                target_trend_active=True,
                candidate_terminally_invalidated=(
                    event.terminal and event.break_state is BreakState.TRUE_BREAK),
                cutoff=bar.close_time)
            counter['update008_calls']+=1
            if episode is not None:
                # This can arise from source evidence; NOT proof of B5 market use.
                counter['anchor_episodes']+=1
        last_d2=_feed_one_source_bar(bar,900000,segment)
        trend=last_d2.update_006_trend
        if trend.episode_id is not None:
            counter['actual_15m_trend_episodes']+=1
        # D4 no-mechanism fail-closed diagnostic only. This uses only actual
        # original D3 event IDs; never manufactures mechanism evidence.
        if same_bar_d3_events and trend.episode_id is not None:
            chosen=next((e for e in same_bar_d3_events
               if e.target_trend_episode_id==trend.episode_id and
                  e.target_direction is trend.direction),None)
            if chosen is not None:
                d4_input=D4CutoffInput(
                    information_cutoff=bar.close_time,
                    trend=trend,
                    trend_position=last_d2.update_009_trend_position,
                    opportunity_direction=trend.direction,
                    market_event_id=chosen.event_id,
                    detector_evidence_ids=(),
                    critical_information_known=InfoValue.unknown(),
                    entry_boundary_unit=None,anchor_episodes={},
                    parameters=frozen_d4_parameters(snapshot))
                no_mechanism=update_011(d4_input)
                if (no_mechanism.confirmation_candidate is not None or
                    no_mechanism.opportunity is not None):
                    raise ValueError('UNAUTHORIZED_D4_CONFIRMATION_FROM_NO_EVIDENCE')
                diagnostic_d4_calls+=1
        complete_sources={900000:bar}
        # Source_TF aggregation: only a fully complete 1H/4H 15m segment;
        # the already closed 15m bar T ends the target exact bucket.
        for ms in (3600000,14400000):
            if (bar.close_time+1)%ms:
                continue
            required=ms//900000
            if i+1<required:
                continue
            htfs=aggregate_completed_htf(
                d1.records[i+1-required:i+1],timeframe_ms=ms,
                information_cutoff=bar.close_time)
            if not htfs:
                continue
            if len(htfs)!=1 or htfs[0].close_time!=bar.close_time:
                raise ValueError('HTF_CAUSAL_COMPLETION_MISMATCH')
            _feed_one_source_bar(htfs[0],ms,segment)
            complete_sources[ms]=htfs[0]
        # Every source candidate registered post-close, never on same bar.
        for ms,source_bar in complete_sources.items():
            _register_candidates(source_bar,ms,trend)
        trend_episode_before=trend.episode_id
        trend_direction_before=trend.direction
    # True B5 requires authenticated causal contact zones, qualified post-
    # resolution Minor progress and structural suitability. None is forged.
    # Call original zero-input role code to preserve empty evidence semantics.
    counter['d4_no_mechanism_diagnostic_calls']=diagnostic_d4_calls
    b5_units=cluster_units([])
    b5_roles=assign_roles([],structural_suitable_unit_ids=set())
    if b5_units or b5_roles.primary_unit_id is not None:
        raise ValueError('UNAUTHORIZED_B5_ROLE_FROM_EMPTY_EVIDENCE')
    # D4 actual original update_011 is called only with a D3 source event ID,
    # no mechanism or detector evidence, and critical-info UNKNOWN. This does
    # NOT make event authority or qualified mechanism evidence; it can only
    # exercise the original no-mechanism fail-closed branch.
    return {'schema':'TAC_ORIGINAL_D3_MULTITF_TEST_ONLY_V1',
      'status':'PARTIAL_ORIGINAL_15M_1H_4H_D3_CAUSAL_STAGE_EXECUTED',
      'symbol':symbol,'cutoff':d1.information_cutoff,
      'counts':counter,
      'last_d2_trend':last_d2.update_006_trend.direction.value,
      'D3_confirmed_return_and_structural_acceptance':'NOT_AUTHENTICATED',
      'B5_primary_unit_id':b5_roles.primary_unit_id,
      'B5_secondary_unit_id':b5_roles.secondary_unit_id,
      'D4':'NO_MECHANISM_DIAGNOSTIC_ONLY_NO_ENTRY_SIGNAL',
      'F9_D5_UPDATE014_D6':'NOT_CONNECTED',
      'entry_ready':False,'trade_authorized':False,
      'TAC_LIVE_ENABLED':0,'orders':0,'fills':0}
