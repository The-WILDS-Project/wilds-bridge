"""
Minimal but structurally complete XML fixtures for each model.
Values are plausible but not necessarily real observations.
"""

# Field order matches the XSD element order (required for pydantic-xml ordered parsing).

TCS_TELEMETRY_XML = """\
<TCSTelemetry>
  <TimeStamp>1733652000</TimeStamp>
  <TCSLST>04:41:18.100</TCSLST>
  <TCSUTC>2024-12-08T06:59:59.893Z</TCSUTC>
  <DemandRa>05:34:32.0</DemandRa>
  <DemandDec>+22:00:52.0</DemandDec>
  <CurrentHourAngle>00:00:07</CurrentHourAngle>
  <TCSCurrentZenithDistance>28.5</TCSCurrentZenithDistance>
  <TCSCurrentAzimuth>175.3</TCSCurrentAzimuth>
  <TCSCurrentElev>61.5</TCSCurrentElev>
  <MountGuideMode>ClosedLoop</MountGuideMode>
  <ScienceTargetName>Crab Nebula</ScienceTargetName>
  <m1CoverState>Open</m1CoverState>
  <MountDomeAzimuthDifference>2.1</MountDomeAzimuthDifference>
  <DomeOccultationWarning>false</DomeOccultationWarning>
  <CurrentParAngle>-12.34</CurrentParAngle>
  <TCSCurrentRotatorPA>90.0</TCSCurrentRotatorPA>
  <TCSCurrentRotatorIAA>4.95</TCSCurrentRotatorIAA>
  <TCSCurrentRotatorIPA>0.0</TCSCurrentRotatorIPA>
  <RotatorFrame>Target</RotatorFrame>
  <TargetFrame>FK5</TargetFrame>
  <equinox>2000.0</equinox>
  <TCSState>ENABLED</TCSState>
  <TCSHealth>GOOD</TCSHealth>
  <TCSHeartBeat>42</TCSHeartBeat>
  <TCSAccessMode>Operator</TCSAccessMode>
  <InPosition>true</InPosition>
  <MountTemperature>7.5</MountTemperature>
  <CLSLowBankState>On</CLSLowBankState>
  <DSSPositionStatus>Open</DSSPositionStatus>
</TCSTelemetry>"""

# Minimal variant — optional fields absent (tests default=None handling)
TCS_TELEMETRY_XML_MINIMAL = """\
<TCSTelemetry>
  <TimeStamp>1733652001</TimeStamp>
  <TCSLST>04:41:19.100</TCSLST>
  <TCSUTC>2024-12-08T07:00:00.893Z</TCSUTC>
  <DemandRa>05:34:32.0</DemandRa>
  <DemandDec>+22:00:52.0</DemandDec>
  <CurrentHourAngle>00:00:08</CurrentHourAngle>
  <TCSCurrentZenithDistance>28.5</TCSCurrentZenithDistance>
  <TCSCurrentAzimuth>175.3</TCSCurrentAzimuth>
  <TCSCurrentElev>61.5</TCSCurrentElev>
  <ScienceTargetName>Crab Nebula</ScienceTargetName>
  <m1CoverState>Open</m1CoverState>
  <DomeOccultationWarning>false</DomeOccultationWarning>
  <CurrentParAngle>-12.34</CurrentParAngle>
  <TCSState>ENABLED</TCSState>
  <TCSHealth>GOOD</TCSHealth>
  <TCSHeartBeat>43</TCSHeartBeat>
  <TCSAccessMode>Operator</TCSAccessMode>
  <InPosition>false</InPosition>
</TCSTelemetry>"""

TCS_STATUS_XML = """\
<tcsTCSStatus>
  <tcsVersion>V1.9</tcsVersion>
  <accessMode>Operator</accessMode>
  <azCurrentWrap>-1</azCurrentWrap>
  <heartbeat>100</heartbeat>
  <inPositionIsTrue>true</inPositionIsTrue>
  <m1CoverState>Open</m1CoverState>
  <mountGuideMode>ClosedLoop</mountGuideMode>
  <rotCurrentWrap>-1</rotCurrentWrap>
  <tcsHealth>GOOD</tcsHealth>
  <tcsState>ENABLED</tcsState>
  <currentTimes>
    <lst>
      <hours>4</hours>
      <minutesTime>41</minutesTime>
      <secondsTime>18.1</secondsTime>
    </lst>
    <time>2026-04-29T07:00:00.000+00:00</time>
  </currentTimes>
  <limits>
    <moonProximity>
      <distance_deg>45.2</distance_deg>
      <proximityFlag>false</proximityFlag>
    </moonProximity>
    <sunProximity>
      <distance_deg>38.5</distance_deg>
      <proximityFlag>false</proximityFlag>
    </sunProximity>
    <zenith>
      <currentZD_deg>28.5</currentZD_deg>
      <elZenithLimit_deg>89.3</elZenithLimit_deg>
      <inBlindSpotIsTrue>false</inBlindSpotIsTrue>
      <timeToBlindSpot_min>-1</timeToBlindSpot_min>
      <timeToBlindSpotExit_min>-1</timeToBlindSpotExit_min>
    </zenith>
    <airmass>1.143</airmass>
    <currentTimeToObservable_min>-1</currentTimeToObservable_min>
    <currentTimeToUnobservable_min>582</currentTimeToUnobservable_min>
    <timeToRotLimit_min>-1</timeToRotLimit_min>
    <timeToAzLimit_min>605.3</timeToAzLimit_min>
  </limits>
  <pointingPositions>
    <azElError>
      <azError>-0.5</azError>
      <elError>-0.6</elError>
    </azElError>
    <currentAzEl>
      <azimuth>
        <degreesArc>175</degreesArc>
        <minutesArc>17</minutesArc>
        <secondsArc>60.0</secondsArc>
      </azimuth>
      <elevation>
        <degreesAlt>61</degreesAlt>
        <minutesArc>30</minutesArc>
        <secondsArc>0.0</secondsArc>
      </elevation>
    </currentAzEl>
    <currentHA>
      <hours>0</hours>
      <minutesTime>0</minutesTime>
      <secondsTime>7.0</secondsTime>
    </currentHA>
    <currentRADec>
      <declination>
        <degreesDec>22</degreesDec>
        <minutesArc>0</minutesArc>
        <secondsArc>52.0</secondsArc>
      </declination>
      <equinoxPrefix>J</equinoxPrefix>
      <equinoxYear>2000.0</equinoxYear>
      <frame>FK5</frame>
      <ra>
        <hours>5</hours>
        <minutesTime>34</minutesTime>
        <secondsTime>32.0</secondsTime>
      </ra>
    </currentRADec>
    <currentParAngle>-12.34</currentParAngle>
    <currentRotatorPositions>
      <rotPA>225.8</rotPA>
      <iaa>6</iaa>
      <rotIPA>0</rotIPA>
    </currentRotatorPositions>
    <targetName>Crab Nebula</targetName>
  </pointingPositions>
  <OffsetStatus>
    <offsetType>SIMPLE</offsetType>
    <userOff1>0</userOff1>
    <userOff2>0</userOff2>
    <handsetOff1>0.4</handsetOff1>
    <handsetOff2>0</handsetOff2>
  </OffsetStatus>
  <axesTrackMode>All</axesTrackMode>
  <inPositionAzIsTrue>true</inPositionAzIsTrue>
  <inPositionElIsTrue>true</inPositionElIsTrue>
  <inPositionRotIsTrue>true</inPositionRotIsTrue>
</tcsTCSStatus>"""

WRS_TELEMETRY_XML = """\
<wrsTelemetry>
  <Timestamp>1733652000</Timestamp>
  <AirTemp>5.2</AirTemp>
  <BarometricPressure>820.1</BarometricPressure>
  <DewPoint>-3.1</DewPoint>
  <RelativeHumidity>42.0</RelativeHumidity>
  <WindDirection>270.0</WindDirection>
  <WindSpeed>3.5</WindSpeed>
</wrsTelemetry>"""

WRS_TELEMETRY_XML_MINIMAL = """\
<wrsTelemetry>
  <Timestamp>1733652001</Timestamp>
</wrsTelemetry>"""

WRS_DATA_PACKET_XML = """\
<WRSDataPacket>
  <airTemp_C>7.3</airTemp_C>
  <barPressure_mbar>1025.0</barPressure_mbar>
  <dewPointCurrentValue>-2.1</dewPointCurrentValue>
  <rainRate>0.0</rainRate>
  <relativeHumidity>28.0</relativeHumidity>
  <timestamp>2018-09-29T01:43:29.000+00:00</timestamp>
  <temperatureStatistics>
    <max>9.1</max>
    <min>6.8</min>
    <mean>7.9</mean>
  </temperatureStatistics>
  <tempRateOfChange_C>-0.4</tempRateOfChange_C>
  <windDirection_deg>294.0</windDirection_deg>
  <windSpeed>3.2</windSpeed>
  <tenMinWindGustSpeed>5.8</tenMinWindGustSpeed>
  <windSpeedStatistics>
    <max>6.1</max>
    <min>1.5</min>
    <mean>3.4</mean>
  </windSpeedStatistics>
</WRSDataPacket>"""

AOS_DATA_PACKET_XML = """\
<AOSDataPacket>
  <timestamp>2018-09-29T06:09:34.662+00:00</timestamp>
  <detailedState>ClosedLoopState</detailedState>
  <summaryState>Enabled</summaryState>
  <tipTiltPistonDemandM1>
    <X_Tilt_rad>0.0</X_Tilt_rad>
    <Y_Tilt_rad>0.0</Y_Tilt_rad>
    <Piston_m>0.0</Piston_m>
  </tipTiltPistonDemandM1>
  <tipTiltPistonDemandM2>
    <X_Tilt_rad>-0.000211</X_Tilt_rad>
    <Y_Tilt_rad>0.000193</Y_Tilt_rad>
    <Piston_m>0.000416</Piston_m>
  </tipTiltPistonDemandM2>
  <comaPointingOffset>
    <xCorrection_arcsec>-23.49</xCorrection_arcsec>
    <yCorrection_arcsec>-25.69</yCorrection_arcsec>
  </comaPointingOffset>
  <totalFocusOffset>0.001195</totalFocusOffset>
  <focusOffsetDemandOutOfRange>false</focusOffsetDemandOutOfRange>
  <wavefrontDataOutOfRange>false</wavefrontDataOutOfRange>
  <M1FSettled>true</M1FSettled>
  <M1LSettled>true</M1LSettled>
  <M1PSettled>true</M1PSettled>
  <M2PSettled>true</M2PSettled>
  <M2VSettled>true</M2VSettled>
</AOSDataPacket>"""

INSTRUMENT_CUBE_XML = """\
<InstrumentCubeTelemetry>
  <TimeStamp>1581440388</TimeStamp>
  <InstrumentCoverState>Open</InstrumentCoverState>
  <InstrumentCoverPosition>-3.22</InstrumentCoverPosition>
  <FMAState>Home</FMAState>
  <FMAPosition>0.0</FMAPosition>
  <FMBState>Home</FMBState>
  <FMBPosition>0.0</FMBPosition>
  <FMCState>Extended</FMCState>
  <FMCPosition>12.5</FMCPosition>
  <FMDState>Home</FMDState>
  <FMDPosition>0.0</FMDPosition>
</InstrumentCubeTelemetry>"""

WILDS_TELEMETRY_XML = """\
<wildsTelemetry>
  <Timestamp>1733652000</Timestamp>
  <SlitPositionMM>12.5</SlitPositionMM>
  <SlitPositionASEC>1.25</SlitPositionASEC>
  <ADC1PositionMM>5.0</ADC1PositionMM>
  <ADC2PositionMM>7.3</ADC2PositionMM>
  <ADCParAngleDeg>-12.34</ADCParAngleDeg>
  <Shutter1State>Open</Shutter1State>
  <VISExposureState>EXPOSING</VISExposureState>
  <VISExposureTime>300.0</VISExposureTime>
  <VISCCDTemp>-110.0</VISCCDTemp>
  <UVExposureState>EXPOSING</UVExposureState>
  <UVExposureTime>300.0</UVExposureTime>
  <UVCCDTemp>-110.0</UVCCDTemp>
  <GuideCameraState>GUIDING</GuideCameraState>
  <LastFITSFileVIS>/data/wilds/2024/vis_001.fits</LastFITSFileVIS>
  <LastFITSFileUV>/data/wilds/2024/uv_001.fits</LastFITSFileUV>
</wildsTelemetry>"""

TCS_OFFSET_COMMAND_XML = """\
<scienceTargetOffset>
  <commandID>59909236</commandID>
  <tcsErrorResponse>
    <code>0</code>
    <source/>
    <status>false</status>
  </tcsErrorResponse>
  <offsetDef>
    <num1>User</num1>
    <off1>-8.133</off1>
    <off2>12.0</off2>
    <offsetType>TPLANE</offsetType>
  </offsetDef>
</scienceTargetOffset>"""

TCS_CLEAR_OFFSET_XML = """\
<scienceTargetClearOffset>
  <commandID>762271817</commandID>
  <tcsErrorResponse>
    <code>0</code>
    <source/>
    <status>false</status>
  </tcsErrorResponse>
  <num2>User</num2>
</scienceTargetClearOffset>"""
