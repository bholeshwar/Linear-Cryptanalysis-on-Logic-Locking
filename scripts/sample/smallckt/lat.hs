
xori :: Bool -> Bool -> Bool
xori x y
	| x == y = False
	| otherwise = True

ori :: Bool -> Bool -> Bool
ori x y = x || y

andi :: Bool -> Bool -> Bool
andi x y = x && y

noti :: Bool -> Bool
noti x
	| x == True = False
	| otherwise = True

enc :: (Bool,Bool,Bool,Bool,Bool,Bool,Bool,Bool,Bool) -> (Bool,Bool,Bool)
enc (a1,a2,a3,a4,a5,k1,k2,k3,k4)=((ori (xori k1 (andi a1 a2)) (xori k1 (noti (andi a2 a3)))) ,xori k3 (ori a4 (andi a1 a2)) ,xori k4 (ori (a4 && a5) (xori k2 (noti (a2 && a3)))) )

out :: (Bool,Bool,Bool,Bool,Bool) -> (Bool,Bool,Bool)
out (a1,a2,a3,a4,a5) = ((noti (a1 && a2))||(noti (a2 && a3)) , noti (a4 || (a1 && a2)) ,noti ((a4 && a5)||(noti (a2 && a3))) )

booltoint :: Bool -> Int
booltoint x
	| x == True = 1
	| otherwise = 0

inttobool :: Int -> Bool
inttobool x
	| x==1 = True
	| otherwise = False

booltointi :: (Bool , Bool , Bool) -> (Int,Int,Int)
booltointi (x1,x2,x3) = (booltoint x1,booltoint x2,booltoint x3)

gout :: (Int,Int,Int,Int,Int) -> (Int,Int,Int)
gout (x1,x2,x3,x4,x5) = booltointi (out (inttobool x1,inttobool x2,inttobool x3,inttobool x4,inttobool x5))

genc :: (Int,Int,Int,Int,Int,Int,Int,Int,Int) -> (Int,Int,Int)
genc (a1,a2,a3,a4,a5,k1,k2,k3,k4) = booltointi (enc (inttobool a1,inttobool a2,inttobool a3, inttobool a4,inttobool a5, inttobool k1,inttobool k2 ,inttobool k3, inttobool k4))

chec :: (Int,Int,Int,Int,Int) -> (Int,Int,Int) -> [((Int,Int,Int,Int,Int),(Int,Int,Int))] -> Int
chec (a1,a2,a3,a4,a5) (b1,b2,b3) [] = 0
chec (a1,a2,a3,a4,a5) (b1,b2,b3) (((aa1,aa2,aa3,aa4,aa5),(bb1,bb2,bb3)):xs) = booltoint ( (mod (a1*aa1+a2*aa2+a3*aa3+a4*aa4+a5*aa5) 2)  == ( mod (b1*bb1+b2*bb2+b3*bb3) 2) ) + (chec (a1,a2,a3,a4,a5) (b1,b2,b3) xs)

bin3 :: Int -> (Int,Int,Int)
bin3 x = ( mod (quot x 4) 2,mod (quot x 2) 2 ,mod x 2 )

bin4 :: Int -> (Int,Int,Int,Int)
bin4 x = ( mod (quot x 8) 2,mod (quot x 4) 2,mod (quot x 2) 2 ,mod x 2 )

bin5 :: Int -> (Int,Int,Int,Int,Int)
bin5 x = (mod (quot x 16) 2, mod (quot x 8) 2,mod (quot x 4) 2,mod (quot x 2) 2 ,mod x 2 )

conv :: (Int,Int) -> ((Int,Int,Int,Int,Int),(Int,Int,Int))
conv (x,y) = (bin5 x,bin3 y)

lit = map conv [(x,y)|x<-[0..31],y<-[0..7]]

randominlist :: [(Int, Int, Int, Int, Int)]
randominlist = [(0,1,1,1,1), (1,1,0,0,1), (1,1,1,1,1), (0,0,0,0,0), (0,1,0,0,0), (0,1,0,0,1), (0,0,1,1,0), (0,0,1,0,1), (1,0,1,0,0), (0,0,1,1,1), (0,1,1,0,1), (1,0,0,1,1), (1,1,1,1,0), (0,0,0,1,0), (1,0,0,1,0), (1,1,1,0,1), (0,0,1,0,0), (1,0,0,0,1), (1,0,1,1,0), (1,1,0,0,1)]

randomoutlist :: [(Int, Int, Int)]
randomoutlist = map gout randominlist

rand = zip randominlist randomoutlist

final = [ (chec (fst a) (snd a) rand) - 10| a <- lit]

xora4b2 :: (Int,Int,Int,Int,Int) -> (Int,Int,Int) -> Bool
xora4b2 (a1,a2,a3,a4,a5) (b1,b2,b3) = (xori (inttobool a4) (inttobool b2) == True)

xor13 :: (Int,Int,Int) -> Bool
xor13 (b1,b2,b3) = ((xori (inttobool b1) (inttobool b3)) == True)

xorb1 :: (Int,Int,Int) -> Bool
xorb1 (b1,b2,b3) = ( b1 == 1)

xorb3 :: (Int,Int,Int) -> Bool
xorb3 (b1,b2,b3) = (b3 == 0)

checkc :: (Int,Int,Int,Int) -> [(Int,Int,Int,Int,Int)] -> Int
checkc (k1,k2,k3,k4) [] = 0
checkc (k1,k2,k3,k4) ((a1,a2,a3,a4,a5):xs) = (booltoint (xor13 ( (genc (a1,a2,a3,a4,a5,k1,k2,k3,k4))))) + checkc (k1,k2,k3,k4) xs

checkb1 :: (Int,Int,Int,Int) -> [(Int,Int,Int,Int,Int)] -> Int
checkb1 (k1,k2,k3,k4) [] = 0
checkb1 (k1,k2,k3,k4) ((a1,a2,a3,a4,a5):xs) = (booltoint (xorb1 ( (genc (a1,a2,a3,a4,a5,k1,k2,k3,k4))))) + checkb1 (k1,k2,k3,k4) xs

checkb3 :: (Int,Int,Int,Int) -> [(Int,Int,Int,Int,Int)] -> Int
checkb3 (k1,k2,k3,k4) [] = 0
checkb3 (k1,k2,k3,k4) ((a1,a2,a3,a4,a5):xs) = (booltoint (xorb3 ( (genc (a1,a2,a3,a4,a5,k1,k2,k3,k4))))) + checkb3 (k1,k2,k3,k4) xs

checkca :: (Int,Int,Int,Int) -> [(Int,Int,Int,Int,Int)] -> Int
checkca (k1,k2,k3,k4) [] = 0
checkca (k1,k2,k3,k4) ((a1,a2,a3,a4,a5):xs) = (booltoint (xora4b2 (a1,a2,a3,a4,a5) ( (genc (a1,a2,a3,a4,a5,k1,k2,k3,k4))))) + checkca (k1,k2,k3,k4) xs


probb1 = [checkb1 k randominlist|k<-(map bin4 [0..15])]
probca = [checkc k randominlist|k<-(map bin4 [0..15])]
probb3 = [checkb3 k randominlist|k<-(map bin4 [0..15])] 
proba4b2 = [checkca k randominlist|k<-(map bin4 [0..15])]
 



