
function [ccdimginfo] = detectorinfo(ccdimginfo)
% 
% DETECTORINFO Load some detector related parameters to ccdimginfo
%
% Michael Sprung
% $Revision: 1.0 $Date: 2005/09/13 $
% $Revision: 2.0 $Date: 2006/11/16 $
% 
% Correction files like blemish & flatfield are included now
% Correction files like distortion & parasitic are still not enabled 
%


% =========================================================================
% --- Detector 1 : Direct Detection CCD in slow mode
% =========================================================================
if ( ccdimginfo.detector == 1 )
    ccdimginfo.ccdHardwareColSize = 1242                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1152                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          = -1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.0225                                 ; % pixel size in mm
    ccdimginfo.saturation         = 65535                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 476                                    ; % adu per photon @ 7.6keV
    ccdimginfo.efficiency         = 0.28                                   ; % efficiency @ 7.6keV
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ; % uses blemish file   (see 'getblemish.m')
    ccdimginfo.flatfield          = 1                                      ; % uses flatfiled file (see 'getflatfield.m')
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = -15                                    ;
end
% value,defaults,"rdfunc-1",  "collectimg_long"


% =========================================================================
% --- Detector 2 : Direct Detection CCD in fast mode
% =========================================================================
if ( ccdimginfo.detector == 2 )
    ccdimginfo.ccdHardwareColSize = 1242                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1152                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          = -1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.0225                                 ; % pixel size in mm
    ccdimginfo.saturation         = 4095                                   ; % saturation count in one pixel
    ccdimginfo.adupphot           = 90                                     ; % adu per photon @ 6.6keV
    ccdimginfo.efficiency         = 0.45                                   ; % efficiency @ 6.6keV
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 1                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = -15                                    ;
end
% value,defaults,"rdfunc-2",  "collectimg"


% =========================================================================
% --- Detector 3 : Capillary Tapered Phosphor CCD 1st Harmonic
% =========================================================================
if ( ccdimginfo.detector == 3 )
    ccdimginfo.ccdHardwareColSize = 1242                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1152                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          = -1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.054                                  ; % pixel size in mm
    ccdimginfo.saturation         = 65535                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 0.755                                  ; % adu per photon
    ccdimginfo.efficiency         = 1.00                                   ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.distortion         = ''                                     ;
    ccdimginfo.blemish            = 0                                      ;
    ccdimginfo.flatfield          = 1                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = -15                                    ;
end
%  value,defaults,"rdfunc-3",     "collectimg_long"
%  value,defaults,"distortion-3", detectordirectory+"meshes.b"
   

% =========================================================================
% --- Detector 4 : Capillary Tapered Phosphor CCD 3rd Harmonic
% =========================================================================
if ( ccdimginfo.detector == 4 )
    ccdimginfo.ccdHardwareColSize = 1242                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1152                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          = -1                                     ;
    ccdimginfo.harmonic           = 3                                      ;
    ccdimginfo.dpix               = 0.054                                  ; % pixel size in mm
    ccdimginfo.saturation         = 65535                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 2.265                                  ; % adu per photon
    ccdimginfo.efficiency         = 0.39                                   ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.distortion         = ''                                     ;
    ccdimginfo.blemish            = 0                                      ;
    ccdimginfo.flatfield          = 1                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = -15                                    ;
end
%  value,defaults,"rdfunc-4",     "collectimg_long"
%  value,defaults,"distortion-4", detectordirectory+"meshes.b"



% =========================================================================
% --- Detector 5 : DALSA
% =========================================================================
if ( ccdimginfo.detector == 5 )
    ccdimginfo.ccdHardwareColSize = 1024                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1024                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = 1                                      ;
    ccdimginfo.ccdzsense          = -1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.014                                  ; % pixel size in mm
    ccdimginfo.saturation         = 4095                                   ; % saturation count in one pixel
    ccdimginfo.adupphot           = 75.6                                   ; % adu per photon
    ccdimginfo.efficiency         = 0.40                                   ;
    ccdimginfo.gain               = 4                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 4                                      ;
end
% value,defaults,"rdfunc-5",  "collectimg"


% =========================================================================
% --- Detector 6 : SMD CCD 1st Harmonic four times gain
% =========================================================================
if ( ccdimginfo.detector == 6 )
    ccdimginfo.ccdHardwareColSize = 1024                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1024                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          =  1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.014                                  ; % pixel size in mm
    ccdimginfo.saturation         = 4095                                   ; % saturation count in one pixel
    ccdimginfo.adupphot           = 116.0                                  ; % adu per photon [29 *4(Gain)]- SN 06122008
%    ccdimginfo.adupphot           = 75.6                                   ; % adu per photon [18.9 * 4 (Gain)] no '/gain' in normalization
    ccdimginfo.efficiency         = 0.20                                   ;
    ccdimginfo.gain               = 4                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 0                                      ; % MS 032008 new chip
%     ccdimginfo.flatfield          = 1                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 4                                      ;
end
% value,defaults,"rdfunc-6",    "collectimg"


% =========================================================================
% --- Detector 7 : Other (to be determined)
% =========================================================================
if ( ccdimginfo.detector == 7 )
    ccdimginfo.ccdHardwareColSize = 1340                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1300                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          = -1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.02                                   ; % pixel size in mm
    ccdimginfo.saturation         = 65535                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1                                      ; % adu per photon
    ccdimginfo.efficiency         = 1                                      ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 0                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = -15                                    ;
end
% value,defaults,"rdfunc-7",  "collectimg_long"


% =========================================================================
% --- Detector 8 : PI-LCX 1300x1340
% =========================================================================
if ( ccdimginfo.detector == 8 )
    ccdimginfo.ccdHardwareColSize = 1340                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1300                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          = -1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.020                                  ; % pixel size in mm
    ccdimginfo.saturation         = 65535                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 830                                    ; % adu per photon
    ccdimginfo.efficiency         = 0.550                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = -40                                    ;
end
% value,defaults,"rdfunc-8",  "collectimg_long"


% =========================================================================
% --- Detector 9 : CMOS
% =========================================================================
if ( ccdimginfo.detector == 9 )
    ccdimginfo.ccdHardwareColSize = 1280                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1024                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          =  1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.0067                                 ; % pixel size in mm
    ccdimginfo.saturation         = 4095                                   ; % saturation count in one pixel
    ccdimginfo.adupphot           = 276                                    ; % adu per photon (139 : 1.88 ; 276 : 2.92)
    ccdimginfo.efficiency         = 0.083                                  ;
    ccdimginfo.gain               = 2.92                                   ;
    ccdimginfo.blemish            = 0                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 4                                      ;
end
% value,defaults,"rdfunc-9",  "collectimg_long"


% =========================================================================
% --- Detector 10 : CMOS at 47deg .tilt
% =========================================================================
if ( ccdimginfo.detector == 10 )
    ccdimginfo.ccdHardwareColSize = 1280                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1024                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          =  1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = [0.0067,0.00455]                       ; % pixel size in mm
    ccdimginfo.saturation         = 4095                                   ; % saturation count in one pixel
    ccdimginfo.adupphot           = 268                                    ; % adu per photon (161 : 1.88 ; 268 : 2.92)
    ccdimginfo.efficiency         = 0.0117                                 ;
    ccdimginfo.gain               = 2.92                                   ;
    ccdimginfo.blemish            = 0                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 4                                      ;
end
% value,defaults,"rdfunc-10",  "collectimg_long"



% =========================================================================
% --- Detector 11 : Coolsnap
% =========================================================================
if ( ccdimginfo.detector == 11 )
    ccdimginfo.ccdHardwareColSize = 1392                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1040                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          =  1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = [0.000645,0.000645]                    ; % pixel size in mm (10x magnification)
    ccdimginfo.saturation         = 4095                                   ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1                                      ; % adu per photon
    ccdimginfo.efficiency         = 0.001                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 0                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 0                                      ;
end


% =========================================================================
% --- Detector 12 : Brookhaven IMG files
% =========================================================================
if ( ccdimginfo.detector == 12 )
    ccdimginfo.ccdHardwareColSize = 1024                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1024                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = 1                                      ;
    ccdimginfo.ccdzsense          = 1                                      ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.158                                  ; % pixel size in mm
    ccdimginfo.saturation         = 65535                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1.0                                    ; % adu per photon
    ccdimginfo.efficiency         = 1.0                                    ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 0                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 0                                      ;
end
% value,defaults,"rdfunc-11",  "collectimg_long"

% =========================================================================
% --- Detector 13 : PI-CNM 1300x1340
% =========================================================================
if ( ccdimginfo.detector == 13 )
    ccdimginfo.ccdHardwareColSize = 1340                                   ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1300                                   ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          = -1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.020                                  ; % pixel size in mm
    ccdimginfo.saturation         = 65535                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1000                                    ; % adu per photon
    ccdimginfo.efficiency         = 0.550                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 0                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 4                                    ;
end
% value,defaults,"rdfunc-8",  "collectimg_long"


% =========================================================================
% --- Detector 14 : APS PILATUS DP00221
% =========================================================================
if ( ccdimginfo.detector == 14 )
    ccdimginfo.ccdHardwareColSize = 487                                    ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 195                                    ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          = -1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.172                                  ; % pixel size in mm
    ccdimginfo.saturation         = 2000000                                ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1                                      ; % adu per photon
    ccdimginfo.efficiency         = 1.000                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 1                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 0                                      ;
end
% value,defaults,"rdfunc-8",  "collectimg_long"

% ---
% EOF

% =========================================================================
% --- Detector 15 : APS Detector Pool Fast CCD 
% =========================================================================
if ( ccdimginfo.detector == 15 )
    ccdimginfo.ccdHardwareColSize = 494                                    ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 480                                    ; % define ccd hardware row size
    ccdimginfo.ccdxsense          = -1                                     ;
    ccdimginfo.ccdzsense          = 1                                     ;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.030                                  ; % pixel size in mm
    ccdimginfo.saturation         = 4095                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 316.0                                  ; % Nuwan/Larry 20ms, att4, scaled Fe fluor to 7350
    % use Aug. 2011 number from Larry/Nuwan - Fe fluorescence scaled to 7350 eV
    ccdimginfo.efficiency         = 1.000                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = -20                                      ;
end
% value,defaults,"rdfunc-8",  "collectimg_long"
% =========================================================================
% --- Detector 20 : APS Detector Pool Fast CCD -2 Frame Transfer
% =========================================================================
if ( ccdimginfo.detector == 20 )
    ccdimginfo.ccdHardwareColSize = 960; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 962; % define ccd hardware row size

%    ccdimginfo.ccdxsense          = 1; %for rotated (Lurio) fccd2 position
%    ccdimginfo.ccdzsense          = -1; %for rotated (Lurio) fccd2 position

     ccdimginfo.ccdxsense          = 1; %should be -1 for normal fccd2 position
     ccdimginfo.ccdzsense          = +1; %%should be +1 for normal fccd2 position     
    
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.030                                  ; % pixel size in mm
    ccdimginfo.saturation         = 4095                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 311.0                                  ; % Nuwan/Larry 20ms, att4, scaled Fe fluor to 7350
    % use Aug. 2011 number from Larry/Nuwan - Fe fluorescence scaled to 7350 eV
    ccdimginfo.efficiency         = 1.000                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 4                                      ;
end
% ---
% =========================================================================
% --- Detector 25 : Lambda
% =========================================================================
if ( ccdimginfo.detector == 25 )
    ccdimginfo.ccdHardwareRowSize = 516                                    ; % define ccd hardware row size
    ccdimginfo.ccdHardwareColSize = 1556                                   ; % define ccd hardware col size

    ccdimginfo.ccdxsense          = 1;
    ccdimginfo.ccdzsense          = 1;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.055                                  ; % pixel size in mm
    ccdimginfo.saturation         = 4095                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1.0                                  ; % Nuwan/Larry 20ms, att4, scaled Fe fluor to 7350
    ccdimginfo.efficiency         = 1.000                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 1                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 0                                      ;
end
% ---

% =========================================================================
% --- Detector 30 : Eiger
% =========================================================================
if ( ccdimginfo.detector == 30 ) 
    ccdimginfo.ccdHardwareColSize = 1030                                    ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 514;                                    ; % define ccd hardware row size

    ccdimginfo.ccdxsense          = 1;
    ccdimginfo.ccdzsense          = 1;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.075                                  ; % pixel size in mm
    ccdimginfo.saturation         = 4095                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1.0                                  ; % Nuwan/Larry 20ms, att4, scaled Fe fluor to 7350
    ccdimginfo.efficiency         = 1.000                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 1                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 0                                      ;
end
% =========================================================================
% --- Detector 35 : UFXC_128x256
% =========================================================================
if ( ccdimginfo.detector == 35 )
    ccdimginfo.ccdHardwareColSize = 256                                    ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 128                                    ; % define ccd hardware row size

    ccdimginfo.ccdxsense          = 1;
    ccdimginfo.ccdzsense          = 1;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.075                                  ; % pixel size in mm
    ccdimginfo.saturation         = 3                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1.0                                  ; 
    ccdimginfo.efficiency         = 1.000                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 0                                      ;
end
% ===============VIPIC was 40==========================================================
% --- Detector 45 : RIGAKU500K
% =========================================================================
if ( ccdimginfo.detector == 45 )
    ccdimginfo.ccdHardwareColSize = 512                                    ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1024                                    ; % define ccd hardware row size

    ccdimginfo.ccdxsense          = 1;
    ccdimginfo.ccdzsense          = 1;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.076                                  ; % pixel size in mm (this is by mistake set to 76 um, should be 75 um)
    ccdimginfo.saturation         = 3                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1.0                                  ; 
    ccdimginfo.efficiency         = 1.000                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 0                                      ;
end
% --- Detector 46 : RIGAKU500K_NoGap
% =========================================================================
if ( ccdimginfo.detector == 46 )
    ccdimginfo.ccdHardwareColSize = 512                                    ; % define ccd hardware col size
    ccdimginfo.ccdHardwareRowSize = 1024                                    ; % define ccd hardware row size

    ccdimginfo.ccdxsense          = 1;
    ccdimginfo.ccdzsense          = 1;
    ccdimginfo.harmonic           = 1                                      ;
    ccdimginfo.dpix               = 0.076                                  ; % pixel size in mm
    ccdimginfo.saturation         = 3                                  ; % saturation count in one pixel
    ccdimginfo.adupphot           = 1.0                                  ; 
    ccdimginfo.efficiency         = 1.000                                  ;
    ccdimginfo.gain               = 1                                      ;
    ccdimginfo.blemish            = 1                                      ;
    ccdimginfo.flatfield          = 0                                      ;
    ccdimginfo.distortion         = 0                                      ;
    ccdimginfo.parasitic          = 0                                      ;
    ccdimginfo.lld                = 0                                      ;
end

% =========================================================================

% ---
% EOF
% EOF
