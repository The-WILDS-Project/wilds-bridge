"""
Minimal but structurally complete XML fixtures for each model.
Values are plausible but not necessarily real observations.
"""

TCS_TELEMETRY_XML = """\
<tcsTelemetry>
  <Timestamp>1733652000</Timestamp>
  <TCSLST>04:41:18.100</TCSLST>
  <TCSUTC>2024-12-08T06:59:59.893Z</TCSUTC>
  <DemandRa>05:34:32.0</DemandRa>
  <DemandDec>+22:00:52.0</DemandDec>
  <CurrentHourAngle>00:00:07</CurrentHourAngle>
  <TCSCurrentZenithDistance>28.5</TCSCurrentZenithDistance>
  <TCSCurrentAzimuth>175.3</TCSCurrentAzimuth>
  <TCSCurrentElev>61.5</TCSCurrentElev>
  <TCSCurrentRotatorPA>90.0</TCSCurrentRotatorPA>
  <TCSCurrentRotatorIPA>0.0</TCSCurrentRotatorIPA>
  <TCSCurrentRotatorIAA>0.0</TCSCurrentRotatorIAA>
  <RotatorFrame>Target</RotatorFrame>
  <TargetFrame>FK5</TargetFrame>
  <equinox>2000.0</equinox>
  <TCSState>ENABLED</TCSState>
  <TCSHealth>GOOD</TCSHealth>
  <TCSHeartBeat>42</TCSHeartBeat>
  <TCSAccessMode>Operator</TCSAccessMode>
  <InPosition>true</InPosition>
  <ScienceTargetName>Crab Nebula</ScienceTargetName>
  <CurrentParAngle>-12.34</CurrentParAngle>
  <MountTemperature>7.5</MountTemperature>
  <m1CoverState>Open</m1CoverState>
  <MountDomeAzimuthDifference>2.1</MountDomeAzimuthDifference>
  <DomeOccultationWarning>false</DomeOccultationWarning>
  <CLSLowBankState>On</CLSLowBankState>
  <DSSPositionStatus>Open</DSSPositionStatus>
</tcsTelemetry>"""

# Minimal variant — optional fields absent (tests default=None handling)
TCS_TELEMETRY_XML_MINIMAL = """\
<tcsTelemetry>
  <Timestamp>1733652001</Timestamp>
  <TCSLST>04:41:19.100</TCSLST>
  <TCSUTC>2024-12-08T07:00:00.893Z</TCSUTC>
  <DemandRa>05:34:32.0</DemandRa>
  <DemandDec>+22:00:52.0</DemandDec>
  <CurrentHourAngle>00:00:08</CurrentHourAngle>
  <TCSCurrentZenithDistance>28.5</TCSCurrentZenithDistance>
  <TCSCurrentAzimuth>175.3</TCSCurrentAzimuth>
  <TCSCurrentElev>61.5</TCSCurrentElev>
  <TCSCurrentRotatorPA>90.0</TCSCurrentRotatorPA>
  <TCSCurrentRotatorIPA>0.0</TCSCurrentRotatorIPA>
  <TCSCurrentRotatorIAA>0.0</TCSCurrentRotatorIAA>
  <RotatorFrame>Target</RotatorFrame>
  <TargetFrame>FK5</TargetFrame>
  <equinox>2000.0</equinox>
  <TCSState>ENABLED</TCSState>
  <TCSHealth>GOOD</TCSHealth>
  <TCSHeartBeat>43</TCSHeartBeat>
  <TCSAccessMode>Operator</TCSAccessMode>
  <InPosition>false</InPosition>
  <ScienceTargetName>Crab Nebula</ScienceTargetName>
  <CurrentParAngle>-12.34</CurrentParAngle>
  <m1CoverState>Open</m1CoverState>
  <DomeOccultationWarning>false</DomeOccultationWarning>
</tcsTelemetry>"""

TCS_STATUS_XML = """\
<tcsTCSStatus>
  <tcsVersion>1.8</tcsVersion>
  <accessMode>Operator</accessMode>
  <heartbeat>100</heartbeat>
  <inPositionIsTrue>true</inPositionIsTrue>
  <m1CoverState>Open</m1CoverState>
  <mountGuideMode>ClosedLoop</mountGuideMode>
  <tcsHealth>GOOD</tcsHealth>
  <tcsState>ENABLED</tcsState>
  <pointingPositions>
    <currentRADec>
      <ra>
        <hours>5</hours>
        <minutesTime>34</minutesTime>
        <secondsTime>32.0</secondsTime>
      </ra>
      <declination>
        <degreesArc>22</degreesArc>
        <minutesArc>0</minutesArc>
        <secondsArc>52.0</secondsArc>
      </declination>
      <equinoxPrefix>J</equinoxPrefix>
      <equinoxYear>2000.0</equinoxYear>
      <targetName>Crab Nebula</targetName>
    </currentRADec>
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
    <currentParAngle>-12.34</currentParAngle>
  </pointingPositions>
  <currentTimes>
    <utcTime>07:00:00.0</utcTime>
    <lstTime>04:41:18.1</lstTime>
  </currentTimes>
  <limits>
    <airmass>1.143</airmass>
    <moonProximity>45.2</moonProximity>
  </limits>
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

TCS_COMMAND_XML = """\
<TCSTcsCommand>
  <commandID>59909236</commandID>
  <newTarget>
    <tcsId>0</tcsId>
    <isNewTarget>false</isNewTarget>
  </newTarget>
  <offset>
    <offsetDef>User</offsetDef>
    <off1>-8.133</off1>
    <off2>12.0</off2>
    <offsetType>TPLANE</offsetType>
  </offset>
</TCSTcsCommand>"""
