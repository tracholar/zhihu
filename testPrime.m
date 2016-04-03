function [x,y,x1,y1,x2,y2] = testPrime(n)
x = [];y=[];x1=[];y1=[];x2=[];y2=[];
if nargin<1
    n=10000;
end
for i=500:n
    if(isprime(i))
        x1(end+1)=i*cos(i);
        y1(end+1)=i*sin(i);
    else
        x2(end+1)=i*cos(i);
        y2(end+1)=i*sin(i);
    end
    x(end+1)=i*cos(i);
    y(end+1)=i*sin(i);
end
figure;
plot(x,y,'.');
hold on;
plot(x1,y1,'r.');
hold off;
axis equal;

end

