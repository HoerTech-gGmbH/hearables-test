function accelerometer_only()
    close all;
    clear all;
    serialPortName='COM7';   %name of serial port connected to the headset

    %Plot parameters
    wrapTime=5; %wrap time for plots

    %Accelerometer parameters
    Nbits=14; %accelerometer resolution (fixed for now)
    Gmode=4;  %accelerometer full scale. Valid values: 2, 4, 8 and 16 g
    Fs=800;   %accelerometer sampling frequency. Valid values: 12.5, 25, 50, 100, 200, 400 and 800 Hz
	SAMPLES_IN_SPP_PACKET=80;

    if (Nbits==12)
        if Fs>200
            Fs=200;
        end
        CTRL1=bitshift(round(log(Fs/12.5)/log(2)+2),4); %Low performance mode and Fs
    else
        CTRL1=bitshift(round(log(Fs/12.5)/log(2)+2),4)+4; %High performance mode and Fs
    end
    CTRL6=bitshift(round(log(Gmode)/log(2)-1),4)+4; %ODR/2, low noise and g-scale

    if (connectToHeadset(serialPortName)==0)
        return; %exit program
    end
    
    fprintf('Connected to headset...\n');
    %accelerometerStart(); %start accelerometer logging
    accelerometerStartwithSettings(CTRL1, CTRL6); %start accelerometer logging with CTRL1 and CTRL6 settings
    stayinloop=1;
    x=[];
    y=[];
    z=[];
    status=[];
    timestamps=[];

    figure(1);
    %setfigA4('portrait', 2);

    while (stayinloop)
        if ((stayinloop) && (~isempty(get(gcf,'currentchar'))))
            fprintf('Saving figures and exit...\n')
            stayinloop=0;
            close all;
        end
        if (~stayinloop)
            figure(1);
            %setfigA4('portrait', 2);
            wrapTime=(length(x)+1)/Fs;
        end
        while (serialport.BytesAvailable>(8+3*2*SAMPLES_IN_SPP_PACKET+5)) %enough data for new packet. 8 bytes timestamp + 3*20*2 acc bytes + 5 packet header
            [response header invalid_chars]=receivePacket(); %Get ACC response
            if (sum(header==[hex2dec('19') hex2dec('09') hex2dec('D1')])==3)&&(~isempty(response))&&(invalid_chars==0) %decode header with accelerometer data
                timestamp=(2^56*response(8)+2^48*response(7)+2^40*response(6)+2^32*response(5)+2^24*response(4)+2^16*response(3)+2^8*response(2)+response(1))/32768.0;
                response=(mod(256*response(10:2:end)+response(9:2:end)+2^15, 2^16)-2^15)/2^(16-Nbits); %convert to acceleration value
                x=[x Gmode*response(1:3:end)/(2^(Nbits-1))]; %accelerometer x data in g
                y=[y Gmode*response(2:3:end)/(2^(Nbits-1))]; %accelerometer y data in g
                z=[z Gmode*response(3:3:end)/(2^(Nbits-1))]; %accelerometer z data in g
                status=[status zeros(1, length(response)/3)];
                timestamps=[timestamps timestamp*ones(1, length(response)/3)];
            elseif (sum(header==[hex2dec('19') hex2dec('0A') hex2dec('D1')])==3)&&(~isempty(response))&&(~isempty(status))&&(invalid_chars==0) %decode header with status data
                status(end)=mod(response(1)+1, 3)-1; %0->0, 1->1=beep, 2->-1=bop
            end
        end
        try
            ax1=subplot(3, 1, 1);
            plot((max(0, length(x)-floor(wrapTime*Fs)):length(x)-1)/Fs, x(max(1, end-floor(wrapTime*Fs)+1):end), 'b-');
            hold on
            plot((max(0, length(status)-floor(wrapTime*Fs)):length(status)-1)/Fs, status(max(1, end-floor(wrapTime*Fs)+1):end), 'r-');
            %        plot((max(0, length(timestamps)-floor(wrapTime*Fs)):length(timestamps)-1)/Fs, 0.1*(timestamps(max(1, end-floor(wrapTime*Fs)+1):end)-timestamps(1)), 'm-');
            hold off
            axis([max(0, length(x)/Fs-wrapTime) max((length(x)-1)/Fs, 1/Fs) -1.1*Gmode 1.1*Gmode]);
            title('x-axis');
            xlabel('Time [s]');
            ylabel('Acceleration [g]');
            grid;
            ax2=subplot(3, 1, 2);
            plot((max(0, length(y)-floor(wrapTime*Fs)):length(y)-1)/Fs, y(max(1, end-floor(wrapTime*Fs)+1):end), 'b-');
            hold on
            plot((max(0, length(status)-floor(wrapTime*Fs)):length(status)-1)/Fs, status(max(1, end-floor(wrapTime*Fs)+1):end), 'r-');
            hold off
            axis([max(0, length(y)/Fs-wrapTime) max((length(y)-1)/Fs, 1/Fs) -1.1*Gmode 1.1*Gmode]);
            title('y-axis');
            xlabel('Time [s]');
            ylabel('Acceleration [g]');
            grid;
            ax3=subplot(3, 1, 3);
            plot((max(0, length(z)-floor(wrapTime*Fs)):length(z)-1)/Fs, z(max(1, end-floor(wrapTime*Fs)+1):end), 'b-');
            hold on
            plot((max(0, length(status)-floor(wrapTime*Fs)):length(status)-1)/Fs, status(max(1, end-floor(wrapTime*Fs)+1):end), 'r-');
            hold off
            axis([max(0, length(z)/Fs-wrapTime) max((length(z)-1)/Fs, 1/Fs) -1.1*Gmode 1.1*Gmode]);
            grid;
            title('z-axis');
            xlabel('Time [s]');
            ylabel('Acceleration [g]');
            linkaxes([ax1, ax2, ax3], 'x')
            drawnow;
        catch error
            if (~strcmp(error.identifier, 'MATLAB:class:InvalidHandle'))
                fprintf('Some error occured!!(%s)\n', error.identifier);
            end
        end
        if (~stayinloop)
            accelerometerStop();
            calculatedFs = 1.0*(length(timestamps)-find(diff(timestamps)~=0, 1 ))/(timestamps(end)-timestamps(1));
            fprintf('Calculated Fs = %4.3f Hz\n',calculatedFs)
            print('-dpdf', 'accelerometer.pdf');
            % add time and date here
            csvwriteWithHeader('accelerometer.csv', [(0:length(x)-1)'/calculatedFs x' y' z' status' (timestamps-timestamps(1))'], ...
                {'time[s]' 'x-acceleration [g]' 'y-acceleration [g]' 'z-acceleration [g]' 'status' 'timestamp[s]'});
        end
    end
    fclose(serialport);
    delete(serialport);

    function connected=connectToHeadset(serialPortName)
        try
            serialport = serial(serialPortName, 'BaudRate', 3000000, 'DataBits', 8, 'StopBits', 1, 'Parity', 'none', 'FlowControl', 'hardware', 'InputBufferSize', 128*1024);
            fopen(serialport);
        catch error
            connected=0;
            fprintf('Error opening %s\n', serialPortName);
            fclose(serialport);
            delete(serialport);
            return;
        end
        connected=1;
        return;
    end

    function accelerometerStart()
        sendPacket('D1', '0C', 1); %ACC 1 command
    end

    function accelerometerStartwithSettings(CTRL1, CTRL6)
        sendPacket('D1', '0C', [2, CTRL1, CTRL6]); %ACC 2 command with CTRL1 and CTRL6 settings
    end

    function accelerometerStop()
        sendPacket('D1', '0C', 0); %ACC 0 command
    end

    function sendPacket(packetType, commandID, parameters)
        parameters=mod(parameters+256, 256); %convert negative values
        fwrite(serialport, [hex2dec('19') hex2dec(commandID) hex2dec(packetType) mod(length(parameters), 256) floor(length(parameters)/256) parameters]);
    end

    function [response header invalid_chars]=receivePacket()
        invalid_chars=0;
        while (fread(serialport, 1, 'uint8')~=hex2dec('19')) %read till valid packet type (0x19)
            invalid_chars=invalid_chars+1;
        end
        if invalid_chars~=0
            fprintf('%d invalid chars\n', invalid_chars);
        end
        header=fread(serialport, [1, 4], 'uint8'); %read group_code, command_code and payload length
        payload_len=0;
        if (length(header)==4)
            payload_len=256*header(4)+header(3);
        end
        header=[hex2dec('19') header(1:2)];
        response=[];
        if (payload_len>0)
            response=fread(serialport, [1 payload_len], 'uint8'); %read payload
        end
        return;
    end

    function csvwriteWithHeader(filename, data, headerData)
        headerData=sprintf('%s, ', headerData{:}); %comma seperated headerData
        fid = fopen(filename, 'w');
        %TODO change so that it does not overwrite the existing file
        fprintf(fid, '%s\r\n', headerData(1:end-2)); %write headerdata without last comma
        fclose(fid);
        dlmwrite(filename, data, '-append', 'delimiter', ';'); %append measurement data to file
    end

end